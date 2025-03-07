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
package com.csgroup.auxip.odata;

import java.io.InputStream;
import java.util.List;
import java.util.Locale;

import com.csgroup.auxip.model.repository.Storage;
import com.csgroup.auxip.model.security.AccessControl;

import org.apache.olingo.commons.api.data.ContextURL;
import org.apache.olingo.commons.api.data.Entity;
import org.apache.olingo.commons.api.data.Property;
import org.apache.olingo.commons.api.edm.EdmEntitySet;
import org.apache.olingo.commons.api.edm.EdmComplexType;
import org.apache.olingo.commons.api.edm.EdmProperty;
import org.apache.olingo.commons.api.format.ContentType;
import org.apache.olingo.commons.api.http.HttpHeader;
import org.apache.olingo.commons.api.http.HttpStatusCode;
import org.apache.olingo.server.api.OData;
import org.apache.olingo.server.api.ODataApplicationException;
import org.apache.olingo.server.api.ODataRequest;
import org.apache.olingo.server.api.ODataResponse;
import org.apache.olingo.server.api.ServiceMetadata;
import org.apache.olingo.server.api.deserializer.DeserializerException;
import org.apache.olingo.server.api.processor.ComplexProcessor;
import org.apache.olingo.server.api.processor.ComplexProcessor;
import org.apache.olingo.server.api.serializer.ODataSerializer;
import org.apache.olingo.server.api.serializer.ComplexSerializerOptions;
import org.apache.olingo.server.api.serializer.SerializerException;
import org.apache.olingo.server.api.serializer.SerializerResult;
import org.apache.olingo.server.api.uri.UriInfo;
import org.apache.olingo.server.api.uri.UriParameter;
import org.apache.olingo.server.api.uri.UriResource;
import org.apache.olingo.server.api.uri.UriResourceEntitySet;
import org.apache.olingo.server.api.uri.UriResourceProperty;

public class AuxipComplexProcessor implements ComplexProcessor {

  private OData odata;
  private Storage storage;
  private ServiceMetadata serviceMetadata;

  public AuxipComplexProcessor(Storage storage) {
    this.storage = storage;
  }

  public void init(OData odata, ServiceMetadata serviceMetadata) {
    this.odata = odata;
    this.serviceMetadata = serviceMetadata;

  }

  /*
   * In our example, the URL would be: http://localhost:8080/auxip_service/auxip_service.svc/Products(1)/Name
   * and the response:
   * {
   * 
   * @odata.context: "$metadata#Products/Name",
   * value: "Notebook Basic 15"
   * }
   */
  public void readComplex(ODataRequest request, ODataResponse response,
      UriInfo uriInfo, ContentType responseFormat)
      throws ODataApplicationException, SerializerException {


    // Check the client access role 
    if ( !AccessControl.userCanDealWith(request, uriInfo) )
    {
			int statusCode = HttpStatusCode.UNAUTHORIZED.getStatusCode();
			throw new ODataApplicationException("Unauthorized Request !",statusCode, Locale.ROOT,String.valueOf(statusCode));
    }
          
    // 1. Retrieve info from URI
    // 1.1. retrieve the info about the requested entity set
    List<UriResource> resourceParts = uriInfo.getUriResourceParts();
    // expected entitysets are : Products,Subscriptions and Metrics and should be in the first segment 
    UriResourceEntitySet uriEntityset = (UriResourceEntitySet) resourceParts.get(0);
    EdmEntitySet edmEntitySet = uriEntityset.getEntitySet();
    // the key for the entity
    List<UriParameter> keyPredicates = uriEntityset.getKeyPredicates();

    // 1.2. retrieve the requested (Edm) property
    // the last segment is the Property
    UriResourceProperty uriProperty = (UriResourceProperty) resourceParts.get(resourceParts.size() - 1);
    EdmProperty edmProperty = uriProperty.getProperty();
    String edmPropertyName = edmProperty.getName();
    // in our example, we know we have only primitive types in our model
    EdmComplexType edmPropertyType = (EdmComplexType) edmProperty.getType();

    // 2. retrieve data from backend
    // 2.1. retrieve the entity data, for which the property has to be read
    Entity entity = storage.readEntityData(edmEntitySet, keyPredicates);
    if (entity == null) { // Bad request
      int statusCode = HttpStatusCode.NOT_FOUND.getStatusCode();
			throw new ODataApplicationException("Entity not found",statusCode, Locale.ROOT,String.valueOf(statusCode));
    }

    // 2.2. retrieve the property data from the entity
    Property property = entity.getProperty(edmPropertyName);
    if (property == null) {
      int statusCode = HttpStatusCode.NOT_FOUND.getStatusCode();
			throw new ODataApplicationException("Property not found",statusCode, Locale.ROOT,String.valueOf(statusCode));
    }

    // 3. serialize
    Object value = property.getValue();
    if (value != null) {
      // 3.1. configure the serializer
      ODataSerializer serializer = odata.createSerializer(responseFormat);

      ContextURL contextUrl = ContextURL.with().entitySet(edmEntitySet).navOrPropertyPath(edmPropertyName).build();
      ComplexSerializerOptions options = ComplexSerializerOptions.with().contextURL(contextUrl).build();
      // 3.2. serialize
      SerializerResult serializerResult = serializer.complex(serviceMetadata, edmPropertyType, property, options);
      InputStream propertyStream = serializerResult.getContent();

      // 4. configure the response object
      response.setContent(propertyStream);
      response.setStatusCode(HttpStatusCode.OK.getStatusCode());
      response.setHeader(HttpHeader.CONTENT_TYPE, responseFormat.toContentTypeString());
    } else {
      // in case there's no value for the property, we can skip the serialization
      response.setStatusCode(HttpStatusCode.NO_CONTENT.getStatusCode());
    }
  }

  /*
   * These processor methods are not handled in this tutorial
   */

  public void updateComplex(ODataRequest request, ODataResponse response, UriInfo uriInfo, ContentType requestFormat,
      ContentType responseFormat)
      throws ODataApplicationException, DeserializerException, SerializerException {

        int statusCode = HttpStatusCode.NOT_IMPLEMENTED.getStatusCode();
        throw new ODataApplicationException("Not supported.",statusCode, Locale.ROOT,String.valueOf(statusCode));
  }

  public void deleteComplex(ODataRequest request, ODataResponse response, UriInfo uriInfo)
      throws ODataApplicationException {

        int statusCode = HttpStatusCode.NOT_IMPLEMENTED.getStatusCode();
        throw new ODataApplicationException("Not supported.",statusCode, Locale.ROOT,String.valueOf(statusCode));

  }
}
