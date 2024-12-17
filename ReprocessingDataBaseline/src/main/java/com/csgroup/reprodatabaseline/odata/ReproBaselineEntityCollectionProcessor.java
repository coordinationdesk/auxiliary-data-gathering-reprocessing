/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements. See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership. The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License. You may obtain a copy of the License at
 * 
 * http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
package com.csgroup.reprodatabaseline.odata;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

import org.apache.olingo.commons.api.data.ComplexValue;
import org.apache.olingo.commons.api.data.ContextURL;
import org.apache.olingo.commons.api.data.Entity;
import org.apache.olingo.commons.api.data.EntityCollection;
import org.apache.olingo.commons.api.data.Property;
import org.apache.olingo.commons.api.data.ValueType;
import org.apache.olingo.commons.api.edm.EdmEntitySet;
import org.apache.olingo.commons.api.edm.EdmEntityType;
import org.apache.olingo.commons.api.format.ContentType;
import org.apache.olingo.commons.api.http.HttpHeader;
import org.apache.olingo.commons.api.http.HttpStatusCode;
import org.apache.olingo.server.api.OData;
import org.apache.olingo.server.api.ODataApplicationException;
import org.apache.olingo.server.api.ODataRequest;
import org.apache.olingo.server.api.ODataResponse;
import org.apache.olingo.server.api.ServiceMetadata;
import org.apache.olingo.server.api.processor.EntityCollectionProcessor;
import org.apache.olingo.server.api.serializer.EntityCollectionSerializerOptions;
import org.apache.olingo.server.api.serializer.ODataSerializer;
import org.apache.olingo.server.api.serializer.SerializerException;
import org.apache.olingo.server.api.serializer.SerializerResult;
import org.apache.olingo.server.api.uri.UriInfo;
import org.apache.olingo.server.api.uri.UriParameter;
import org.apache.olingo.server.api.uri.UriResource;
import org.apache.olingo.server.api.uri.UriResourceFunction;
import org.apache.olingo.server.api.uri.UriResourceNavigation;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.util.Pair;

import com.csgroup.reprodatabaseline.datamodels.AuxFile;
import com.csgroup.reprodatabaseline.datamodels.L0Product;

public class ReproBaselineEntityCollectionProcessor implements EntityCollectionProcessor {

  private static final Logger LOG = LoggerFactory.getLogger(ReproBaselineEntityCollectionProcessor.class);
  
  // Using the logger defined in the logback.xml config file in resources to log to a specific file the names of the L0 that have not been found
  // on the database
  private static final Logger LOG_L0_NOT_FOUND = LoggerFactory.getLogger("L0NotFoundOnBase");

  private OData odata;
  private ServiceMetadata srvMetadata;
  private ReproDataBaseline reproBaseline;

  public void init(OData odata, ServiceMetadata serviceMetadata) {
    this.odata = odata;
    this.srvMetadata = serviceMetadata;
  }

  public ReproBaselineEntityCollectionProcessor(ReproDataBaseline reproBaseline) {
    this.reproBaseline = reproBaseline;
  }

  /*
   * This method is invoked when a collection of entities has to be read. (
   * Products / Subscriptions)
   */
  public void readEntityCollection(ODataRequest request, ODataResponse response, UriInfo uriInfo,
      ContentType responseFormat) throws ODataApplicationException, SerializerException {

    LOG.info("Starting readEntityCollection");

    // Check the client access role
    // if ( !AccessControl.userCanDealWith(request, uriInfo) )
    // {
    // throw new ODataApplicationException("Unauthorized Request !",
    // HttpStatusCode.UNAUTHORIZED.getStatusCode(), Locale.ROOT);
    // }

    EdmEntitySet responseEdmEntitySet = null; // we'll need this to build the ContextURL
    EntityCollection responseEntityCollection = null; // we'll need this to set the response body
    EdmEntityType responseEdmEntityType = null;

    // 1st retrieve the requested EntitySet from the uriInfo (representation of the
    // parsed URI)
    List<UriResource> resourceParts = uriInfo.getUriResourceParts();
    int segmentCount = resourceParts.size();

    UriResource uriResource = resourceParts.get(0);
    if (!(uriResource instanceof UriResourceFunction)) {
      int statusCode = HttpStatusCode.NOT_IMPLEMENTED.getStatusCode();
      throw new ODataApplicationException("Only function call is supported, see => /$metadata",
          HttpStatusCode.NOT_IMPLEMENTED.getStatusCode(), Locale.ROOT, String.valueOf(statusCode));
    }
    final UriResourceFunction uriResourceFunction = (UriResourceFunction) uriResource;
    final EntityCollection entityCol = getReprocessingDataBaseline((UriResourceFunction) uriResourceFunction, request);

    // 2nd step: Serialize the response entity
    final EdmEntityType edmEntityType = (EdmEntityType) uriResourceFunction.getFunction().getReturnType().getType();
    final ContextURL contextURL = ContextURL.with().asCollection().type(edmEntityType).build();
    EntityCollectionSerializerOptions opts = EntityCollectionSerializerOptions.with().contextURL(contextURL).build();
    final ODataSerializer serializer = odata.createSerializer(responseFormat);
    final SerializerResult serializerResult = serializer.entityCollection(srvMetadata, edmEntityType, entityCol, opts);

    // 3rd configure the response object
    response.setContent(serializerResult.getContent());
    response.setStatusCode(HttpStatusCode.OK.getStatusCode());
    response.setHeader(HttpHeader.CONTENT_TYPE, responseFormat.toContentTypeString());

    LOG.info("Done");
  }

  private boolean isContNav(UriInfo uriInfo) {
    List<UriResource> resourceParts = uriInfo.getUriResourceParts();
    for (UriResource resourcePart : resourceParts) {
      if (resourcePart instanceof UriResourceNavigation) {
        UriResourceNavigation navResource = (UriResourceNavigation) resourcePart;
        if (navResource.getProperty().containsTarget()) {
          return true;
        }
      }
    }
    return false;
  }

  public EntityCollection getReprocessingDataBaseline(final UriResourceFunction uriResourceFunction,
      ODataRequest request) throws ODataApplicationException {

    LOG.info("Starting >> getReprocessingDataBaseline");

    if ("getReprocessingDataBaseline".equals(uriResourceFunction.getFunctionImport().getName())) {
      // Get the parameter of the function
      int nbParameters = uriResourceFunction.getParameters().size();
      String accessToken = request.getHeader("Authorization").replace("Bearer ", "");
      // TODO instead, pass it to ReproDataBaseline
      this.reproBaseline.setAccessToken(accessToken);

      Map<Pair<String, String>, List<AuxFile>> dataBaselines = new HashMap<>();
      String level0Names = "";
      String start = "";
      String stop = "";
      String mission = "";
      String unit = "";
      String productType = "";

      for (int p = 0; p < nbParameters; p++) {

        UriParameter parameter = uriResourceFunction.getParameters().get(p);
        final String paramName = parameter.getName();
        final String paramValue = parameter.getText().replace("'", "");
        switch (paramName) {
          case "l0_names":
            level0Names = paramValue;
            break;
          case "start":
            start = paramValue;
            break;
          case "stop":
            stop = paramValue;
            break;
          case "mission":
            mission = paramValue;
            break;
          case "unit":
            unit = paramValue;
            break;
          case "product_type":
            productType = paramValue;
            break;
          default:
            break;
        }
      }
      
      String defaultLevel0InformationMessage = "The L0 product name entered in the request was found in the data base. "
      		+ "So, the ADF selection rule has been applied using the sensing start of the corresponding data take.";

      if (nbParameters == 4) {
// TODO: reorganize: the problem is associating the L0 Information message to each L0 Product
        // The different messages agenerated on only two conditions: L0 Product available in RDB or not
        // The solution is to generate two lists of L0 Products, when retrieving them by name:
        // the list of found products, and the list of not found products!
        for (String level0Name : level0Names.split(",")) {

          // TODO: get L0 products from reproDataBaseline or better databaslineRepository
        	List<L0Product> level0Products = this.reproBaseline.getLevel0ProductsByName(level0Name);
        	L0Product level0;
        	String level0InfoMessage = defaultLevel0InformationMessage;
        	
        	if (level0Products != null && !level0Products.isEmpty()) {
        		// The L0Product has been found
        		
        		level0 = level0Products.get(0);
        		
        	} else {
        		// The L0Product has not been found
        		
        		// We create an empty one for the following actions WITHOUT validityStart or validityStop to make it clear it was not found on the data base
        		level0 = new L0Product();
        		level0.setName(level0Name);
        		level0InfoMessage = "Warning : The L0 product name entered in the request was not found in the data base. "
        				+ "So, the ADF selection rule has been applied using the sensing start in the provided product name.";
        		LOG.warn(level0InfoMessage);
        		LOG_L0_NOT_FOUND.warn(level0Name);
        	}
        	
        	// TODO: Call funciton on Reprodatabaseline
			List<AuxFile> auxDataFiles = this.reproBaseline.getReprocessingDataBaseline(level0, mission, unit, productType);
			dataBaselines.put(Pair.of(level0Name, level0InfoMessage), auxDataFiles);
        }

      } else {

        List<L0Product> l0Products = this.reproBaseline.getLevel0Products(start, stop, mission, unit,
            productType);
        for (L0Product product : l0Products) {
          List<AuxFile> auxDataFiles = this.reproBaseline.getReprocessingDataBaseline(product, mission,
              unit, productType);
          dataBaselines.put(Pair.of(product.getName(), defaultLevel0InformationMessage), auxDataFiles);
        }
      }

      // TODO : put in function: buildL0BaslineENtity
      final EntityCollection resultCollection = new EntityCollection();

      // Loop items: Pair <L0Name, warnMessage>, List<AuxFile>
      for (Map.Entry<Pair<String, String>, List<AuxFile>> me : dataBaselines.entrySet()) {
        Entity entity = new Entity();
        Property level0 = new Property("String", "Level0", ValueType.PRIMITIVE, me.getKey().getFirst());

        // Adding the property to the response
        entity.addProperty(level0);
        
    	// Adding the message property to the response
    	Property warningMessage = new Property("String", "Message", ValueType.PRIMITIVE, me.getKey().getSecond());
        entity.addProperty(warningMessage);

        List<ComplexValue> auxDataCollection = new ArrayList<>();
        for (AuxFile auxFile : (List<AuxFile>) me.getValue()) {
          ComplexValue auxData = new ComplexValue();
          auxData.getValue().add(new Property("String", "Name", ValueType.PRIMITIVE, auxFile.FullName));
          auxData.getValue().add(new Property("String", "AuxipLink", ValueType.PRIMITIVE, auxFile.AuxipUrl));
          auxDataCollection.add(auxData);
        }
        Property auxDataFiles = new Property(null, "AuxDataFiles", ValueType.COLLECTION_COMPLEX, auxDataCollection);
        entity.addProperty(auxDataFiles);
        entity.setType("OData.CSC.DataBaseline");

        resultCollection.getEntities().add(entity);
      }

      LOG.info("Ending << getReprocessingDataBaseline");
      return resultCollection;

    } else {
      int statusCode = HttpStatusCode.BAD_REQUEST.getStatusCode();
      throw new ODataApplicationException("Function not implemented", statusCode, Locale.ROOT,
          String.valueOf(statusCode));
    }

  }

}
