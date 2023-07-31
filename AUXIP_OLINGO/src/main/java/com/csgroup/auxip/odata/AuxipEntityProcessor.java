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
import java.util.UUID;
import com.csgroup.auxip.controller.AuxipBeanUtil;
import com.csgroup.auxip.model.jpa.Notification;
import com.csgroup.auxip.model.jpa.CounterType;
import com.csgroup.auxip.model.jpa.Globals;
import com.csgroup.auxip.model.jpa.Subscription;
import com.csgroup.auxip.model.jpa.User;
import com.csgroup.auxip.model.jpa.UserManager;
import com.csgroup.auxip.model.repository.Storage;
import com.csgroup.auxip.model.repository.StorageStatus;
import org.apache.olingo.commons.api.Constants;
import com.csgroup.auxip.model.security.AccessControl;
import org.apache.olingo.commons.api.data.ContextURL;
import org.apache.olingo.commons.api.data.ContextURL.Suffix;
import org.apache.olingo.commons.api.data.Entity;
import org.apache.olingo.commons.api.data.EntityCollection;
import org.apache.olingo.commons.api.data.Link;
import org.apache.olingo.commons.api.edm.EdmElement;
import org.apache.olingo.commons.api.edm.EdmEntitySet;
import org.apache.olingo.commons.api.edm.EdmEntityType;
import org.apache.olingo.commons.api.edm.EdmNavigationProperty;
import org.apache.olingo.commons.api.edm.EdmNavigationPropertyBinding;
import org.apache.olingo.commons.api.format.ContentType;
import org.apache.olingo.commons.api.http.HttpHeader;
import org.apache.olingo.commons.api.http.HttpMethod;
import org.apache.olingo.commons.api.http.HttpStatusCode;
import org.apache.olingo.server.api.OData;
import org.apache.olingo.server.api.ODataApplicationException;
import org.apache.olingo.server.api.ODataLibraryException;
import org.apache.olingo.server.api.ODataRequest;
import org.apache.olingo.server.api.ODataResponse;
import org.apache.olingo.server.api.ServiceMetadata;
import org.apache.olingo.server.api.deserializer.DeserializerException;
import org.apache.olingo.server.api.deserializer.DeserializerResult;
import org.apache.olingo.server.api.deserializer.ODataDeserializer;
import org.apache.olingo.server.api.processor.EntityProcessor;
import org.apache.olingo.server.api.processor.MediaEntityProcessor;
import org.apache.olingo.server.api.serializer.EntitySerializerOptions;
import org.apache.olingo.server.api.serializer.ODataSerializer;
import org.apache.olingo.server.api.serializer.SerializerException;
import org.apache.olingo.server.api.serializer.SerializerResult;
import org.apache.olingo.server.api.uri.UriInfo;
import org.apache.olingo.server.api.uri.UriParameter;
import org.apache.olingo.server.api.uri.UriResource;
import org.apache.olingo.server.api.uri.UriResourceEntitySet;
import org.apache.olingo.server.api.uri.UriResourceNavigation;
import org.apache.olingo.server.api.uri.queryoption.ExpandItem;
import org.apache.olingo.server.api.uri.queryoption.ExpandOption;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.apache.olingo.server.core.uri.parser.Parser;
import org.apache.olingo.server.core.uri.parser.UriParserException;
import org.apache.olingo.server.core.uri.validator.UriValidationException;

public class AuxipEntityProcessor implements EntityProcessor, MediaEntityProcessor {

	private static final Logger LOG = LoggerFactory.getLogger(AuxipEntityProcessor.class);
	private OData odata;
	private ServiceMetadata serviceMetadata;
	private Storage storage;

	public AuxipEntityProcessor(Storage storage) {
		this.storage = storage;
	}

	public void init(OData odata, ServiceMetadata serviceMetadata) {
		this.odata = odata;
		this.serviceMetadata = serviceMetadata;
	}

	/**
	 * This method is invoked when a single entity has to be read.
	 * 
	 * Example for "normal" read operation:
	 * /auxip.svc/Products(56d24660-f5dd-41f8-87ca-d9a5f716f3f6)   
	 *  
	 */
	public void readEntity(ODataRequest request, ODataResponse response, UriInfo uriInfo, ContentType responseFormat)
			throws ODataApplicationException, SerializerException {
		LOG.debug("Starting ReadEntity ...");
		// Check the client access role 
		if ( !AccessControl.userCanDealWith(request, uriInfo) )
		{	
			int statusCode = HttpStatusCode.UNAUTHORIZED.getStatusCode();
			throw new ODataApplicationException("Unauthorized Request !", statusCode, Locale.ROOT,String.valueOf(statusCode));
		}
		EdmEntityType responseEdmEntityType = null; // we'll need this to build the ContextURL
		Entity responseEntity = null; // required for serialization of the response body
		EdmEntitySet responseEdmEntitySet = null; // we need this for building the contextUrl

		// 1st step: retrieve the requested Entity: can be "normal" read operation, or navigation (to-one)
		List<UriResource> resourceParts = uriInfo.getUriResourceParts();
		int segmentCount = resourceParts.size();

		UriResource uriResource = resourceParts.get(0); // in auxip, the first segment is the EntitySet
		if (!(uriResource instanceof UriResourceEntitySet)) {

			int statusCode = HttpStatusCode.NOT_IMPLEMENTED.getStatusCode();
			throw new ODataApplicationException("Only EntitySet is supported", statusCode, Locale.ROOT,String.valueOf(statusCode));

		}

		UriResourceEntitySet uriResourceEntitySet = (UriResourceEntitySet) uriResource;
		EdmEntitySet startEdmEntitySet = uriResourceEntitySet.getEntitySet();

		// Analyze the URI segments
		if (segmentCount == 1) { // no navigation
			responseEdmEntityType = startEdmEntitySet.getEntityType();
			responseEdmEntitySet = startEdmEntitySet; // since we have only one segment

			// 2. step: retrieve the data from backend
			List<UriParameter> keyPredicates = uriResourceEntitySet.getKeyPredicates();
			responseEntity = storage.readEntityData(startEdmEntitySet, keyPredicates);

		}else {
			int statusCode = HttpStatusCode.NOT_IMPLEMENTED.getStatusCode();
			throw new ODataApplicationException("Not supported", statusCode, Locale.ROOT,String.valueOf(statusCode));
		}

		if (responseEntity == null) {
			// this is the case for e.g. DemoService.svc/Categories(4) or DemoService.svc/Categories(3)/Products(999)
			int statusCode = HttpStatusCode.NOT_FOUND.getStatusCode();
			throw new ODataApplicationException("Nothing found.", statusCode, Locale.ROOT,String.valueOf(statusCode));	

		}

		// handle $expand
		ExpandOption expandOption = uriInfo.getExpandOption();
		// in our example: http://localhost:8080/auxip.svc/Products(uuid)?$expand=Attributes
		if(expandOption != null) {
			LOG.debug("Expand Option ON");
			// retrieve the EdmNavigationProperty from the expand expression
			// Note: in our example, we have only one NavigationProperty, so we can directly access it
			EdmNavigationProperty edmNavigationProperty = null;
			ExpandItem expandItem = expandOption.getExpandItems().get(0);
			if(expandItem.isStar()) {
				List<EdmNavigationPropertyBinding> bindings = startEdmEntitySet.getNavigationPropertyBindings();
				// we know that there are navigation bindings
				// however normally in this case a check if navigation bindings exists is done
				if(!bindings.isEmpty()) {
					// can in our case only be 'Category' or 'Products', so we can take the first
					EdmNavigationPropertyBinding binding = bindings.get(0);
					EdmElement property = startEdmEntitySet.getEntityType().getProperty(binding.getPath());
					// we don't need to handle error cases, as it is done in the Olingo library
					if(property instanceof EdmNavigationProperty) {
						edmNavigationProperty = (EdmNavigationProperty) property;
					}
				}
			} else {
				// can be 'Attributes' , 'StringAttributes', ..., 
				UriResource uriResource_expand = expandItem.getResourcePath().getUriResourceParts().get(0);
				// we don't need to handle error cases, as it is done in the Olingo library
				if(uriResource_expand instanceof UriResourceNavigation) {
					edmNavigationProperty = ((UriResourceNavigation) uriResource_expand).getProperty();
				}
			}

			// can be 'Category' or 'Products', no path supported
			// we don't need to handle error cases, as it is done in the Olingo library
			if(edmNavigationProperty != null) {
				LOG.debug("Found Navigation Property ...");
				EdmEntityType expandEdmEntityType = edmNavigationProperty.getType();
				String navPropName = edmNavigationProperty.getName();

				// build the inline data
				Link link = new Link();
				link.setTitle(navPropName);
				link.setType(Constants.ENTITY_NAVIGATION_LINK_TYPE);
				link.setRel(Constants.NS_ASSOCIATION_LINK_REL + navPropName);

				if(edmNavigationProperty.isCollection()){ // in case of Categories(1)/$expand=Products
					// fetch the data for the $expand (to-many navigation) from backend
					// here we get the data for the expand
					EntityCollection expandEntityCollection = storage.getRelatedEntityCollection(responseEntity, expandEdmEntityType);
					if (expandEntityCollection != null) {
						link.setInlineEntitySet(expandEntityCollection);
						link.setHref(expandEntityCollection.getId().toASCIIString());
					}
				} else {  // in case of Products(1)?$expand=Category
					// fetch the data for the $expand (to-one navigation) from backend
					// here we get the data for the expand
					Entity expandEntity = storage.getRelatedEntity(responseEntity, expandEdmEntityType);
					if (expandEntity != null) {
						link.setInlineEntity(expandEntity);
						link.setHref(expandEntity.getId().toASCIIString());
					}
				}

				// set the link - containing the expanded data - to the current entity
				responseEntity.getNavigationLinks().add(link);
			}
		}


		// 3. serialize
		ContextURL contextUrl = null;
		if (isContNav(uriInfo)) {
			contextUrl = ContextURL.with().entitySetOrSingletonOrType(request.getRawODataPath()).
					suffix(Suffix.ENTITY).build();
		} else {
			contextUrl = ContextURL.with().entitySet(responseEdmEntitySet).suffix(Suffix.ENTITY).build();
		}

		EntitySerializerOptions opts = EntitySerializerOptions.with()
				.contextURL(contextUrl)
				.expand(expandOption)
				.build();

		ODataSerializer serializer = this.odata.createSerializer(responseFormat);
		SerializerResult serializerResult = serializer.entity(this.serviceMetadata,
				responseEdmEntityType, responseEntity, opts);

		// 4. configure the response object
		response.setContent(serializerResult.getContent());
		response.setStatusCode(HttpStatusCode.OK.getStatusCode());
		response.setHeader(HttpHeader.CONTENT_TYPE, responseFormat.toContentTypeString());

		LOG.debug("ReadEntity Done");
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

	/*
	 * CreateEntity is used while creating Subscriptions
	 */
	public void createEntity(ODataRequest request, ODataResponse response, UriInfo uriInfo,
			ContentType requestFormat, ContentType responseFormat)
					throws ODataApplicationException, DeserializerException, SerializerException {

		LOG.debug("Started createEntity");

		// Check the client access role 
		if ( !AccessControl.userCanDealWith(request, uriInfo) )
		{
			int statusCode = HttpStatusCode.UNAUTHORIZED.getStatusCode();
			throw new ODataApplicationException("Unauthorized Request !",statusCode, Locale.ROOT,String.valueOf(statusCode));
		}

		// 1. Retrieve the entity type from the URI
		List<UriResource> resourceParts = uriInfo.getUriResourceParts();

		UriResource uriResource = resourceParts.get(0); // in auxip, the first segment is the EntitySet
		if (!(uriResource instanceof UriResourceEntitySet)) {

			int statusCode = HttpStatusCode.NOT_IMPLEMENTED.getStatusCode();
			throw new ODataApplicationException("Only EntitySet is supported",statusCode, Locale.ROOT,String.valueOf(statusCode));

		}

		UriResourceEntitySet uriResourceEntitySet = (UriResourceEntitySet) uriResource;
		EdmEntitySet edmEntitySet = uriResourceEntitySet.getEntitySet();

		if( edmEntitySet.getName().equals(Subscription.ES_NAME) )
		{
			EdmEntityType edmEntityType = edmEntitySet.getEntityType();

			// 2. create the data in backend
			// 2.1. retrieve the payload from the POST request for the entity to create and deserialize it
			InputStream requestInputStream = request.getBody();
			ODataDeserializer deserializer = this.odata.createDeserializer(requestFormat);
			DeserializerResult result = deserializer.entity(requestInputStream, edmEntityType);
			Entity requestEntity = result.getEntity();
			// 2.2 do the creation in backend, which returns the newly created entity
			Entity createdEntity = storage.createSubscription(requestEntity);

			// 3. serialize the response (we have to return the created entity)
			ContextURL contextUrl = ContextURL.with().entitySet(edmEntitySet).build();
			// expand and select currently not supported
			EntitySerializerOptions options = EntitySerializerOptions.with().contextURL(contextUrl).build();

			ODataSerializer serializer = this.odata.createSerializer(responseFormat);
			SerializerResult serializedResponse = serializer.entity(serviceMetadata, edmEntityType, createdEntity, options);

			//4. configure the response object
			response.setContent(serializedResponse.getContent());
			response.setStatusCode(HttpStatusCode.CREATED.getStatusCode());
			response.setHeader(HttpHeader.CONTENT_TYPE, responseFormat.toContentTypeString());

		}else{
			int statusCode = HttpStatusCode.NOT_ACCEPTABLE.getStatusCode();
			throw new ODataApplicationException("Not acceptable.",statusCode, Locale.ROOT,String.valueOf(statusCode));
		}
	}

	public void updateEntity(ODataRequest request, ODataResponse response, UriInfo uriInfo,
			ContentType requestFormat, ContentType responseFormat)
					throws ODataApplicationException, DeserializerException, SerializerException {
		LOG.debug("Starting updateEntity");
		// Check the client access role 
		if ( !AccessControl.userCanDealWith(request, uriInfo) )
		{
			int statusCode = HttpStatusCode.UNAUTHORIZED.getStatusCode();
			throw new ODataApplicationException("Unauthorized Request !",statusCode, Locale.ROOT,String.valueOf(statusCode));

		}
		// 1. Retrieve the entity set which belongs to the requested entity 
		List<UriResource> resourcePaths = uriInfo.getUriResourceParts();
		// Note: only in our example we can assume that the first segment is the EntitySet
		UriResourceEntitySet uriResourceEntitySet = (UriResourceEntitySet) resourcePaths.get(0); 
		EdmEntitySet edmEntitySet = uriResourceEntitySet.getEntitySet();
		EdmEntityType edmEntityType = edmEntitySet.getEntityType();
		LOG.debug("edmEntityType: "+edmEntityType.getName());
		// 2. update the data in backend
		// 2.1. retrieve the payload from the PUT request for the entity to be updated 
		InputStream requestInputStream = request.getBody();
		ODataDeserializer deserializer = this.odata.createDeserializer(requestFormat);
		DeserializerResult result = deserializer.entity(requestInputStream, edmEntityType);
		Entity requestEntity = result.getEntity();

		// 2.2 do the modification in backend
		List<UriParameter> keyPredicates = uriResourceEntitySet.getKeyPredicates();
		// Note that this updateEntity()-method is invoked for both PUT or PATCH operations
		HttpMethod httpMethod = request.getMethod();
		storage.updateEntityData(edmEntitySet, keyPredicates, requestEntity, httpMethod);

		//3. configure the response object
		response.setStatusCode(HttpStatusCode.NO_CONTENT.getStatusCode());
	}

	public void deleteEntity(ODataRequest request, ODataResponse response, UriInfo uriInfo)
			throws ODataApplicationException {
		LOG.debug("Starting deleteEntity");
		// Check the client access role 
		if ( !AccessControl.userCanDealWith(request, uriInfo) )
		{
			int statusCode = HttpStatusCode.UNAUTHORIZED.getStatusCode();
			throw new ODataApplicationException("Unauthorized Request !",statusCode, Locale.ROOT,String.valueOf(statusCode));
		}
		// 1. Retrieve the entity set which belongs to the requested entity 
		List<UriResource> resourcePaths = uriInfo.getUriResourceParts();
		// Note: only in our example we can assume that the first segment is the EntitySet
		UriResourceEntitySet uriResourceEntitySet = (UriResourceEntitySet) resourcePaths.get(0); 
		EdmEntitySet edmEntitySet = uriResourceEntitySet.getEntitySet();

		// 2. delete the data in backend
		List<UriParameter> keyPredicates = uriResourceEntitySet.getKeyPredicates();
		storage.deleteEntityData(edmEntitySet, keyPredicates);

		//3. configure the response object
		response.setStatusCode(HttpStatusCode.NO_CONTENT.getStatusCode());
	}

	/**
	 * This method is used while invoking /Products(uuid)/$value
	 */
	@Override
	public void readMediaEntity(ODataRequest request, ODataResponse response, UriInfo uriInfo, ContentType responseFormat)
			throws ODataApplicationException, ODataLibraryException {

		UserManager userManager = new UserManager();
		User user = userManager.getUser(request);
		
		if (user == null)
		{
			int statusCode = HttpStatusCode.BAD_REQUEST.getStatusCode();
			throw new ODataApplicationException("Can't get user from request, check token",statusCode, Locale.ROOT,String.valueOf(statusCode));
		}
		AccessControl accessControl = new AccessControl(user);

		//this call comes from /Products(uuid)/$value
		final UriResource firstResoucePart = uriInfo.getUriResourceParts().get(0);
		if(firstResoucePart instanceof UriResourceEntitySet) 
		{

			UriResourceEntitySet uriResourceEntitySet = (UriResourceEntitySet) firstResoucePart;
			EdmEntitySet edmEntitySet = uriResourceEntitySet.getEntitySet();

			final Entity entity = storage.readEntityData(edmEntitySet, uriResourceEntitySet.getKeyPredicates());
			if(entity == null) {
				int statusCode = HttpStatusCode.NOT_FOUND.getStatusCode();
				throw new ODataApplicationException("Entity not found",statusCode, Locale.ROOT,String.valueOf(statusCode));
			}
			String productName = (String)entity.getProperty("Name").asPrimitive();
			LOG.debug("ProductName: "+productName);
			// Role & Quota checking
			if( !accessControl.userCanDownload() )
			{
				// update number of failed downloads
				user.incrementDownloadsCounter( productName , CounterType.failed );
				userManager.saveUser();
				userManager.close();

				throw new ODataApplicationException("Too Many Requests !",Globals.TOO_MANY_REQUESTS, Locale.ROOT,String.valueOf(Globals.TOO_MANY_REQUESTS));
			}
			LOG.debug("Access control Granted");

			try {
			// increment the completed downloads counter
			user.incrementDownloadsCounter(productName, CounterType.completed );
			// update downloaded volumes
			long productLength = (long)entity.getProperty("ContentLength").asPrimitive() ;
			user.incrementDownloadsCounter(productName, CounterType.volume , productLength );
			user.updateDownloadedVolume(productLength);
			} catch (Exception e) {
				LOG.error("Error when updating to user profiles");
				int statusCode = HttpStatusCode.INTERNAL_SERVER_ERROR.getStatusCode();
				throw new ODataApplicationException("Error when updating user",statusCode, Locale.ROOT,String.valueOf(statusCode));
			}
			try {

				userManager.saveUser();
				userManager.close();
			} catch (Exception e) {
				LOG.error("Error when committing to user profiles");
				int statusCode = HttpStatusCode.INTERNAL_SERVER_ERROR.getStatusCode();
				throw new ODataApplicationException("Error when committing to user profile",statusCode, Locale.ROOT,String.valueOf(statusCode));
			}
			LOG.debug("User handling done");

			final String mediaContent = entity.getProperty("$value").getValue().toString();
			response.setStatusCode(HttpStatusCode.FOUND.getStatusCode());
			response.setHeader("Content-Disposition", "filename="+entity.getProperty("Name").getValue().toString());
			response.setHeader(HttpHeader.LOCATION, mediaContent);
			LOG.debug("Response Header set, filename: {} ", entity.getProperty("Name").getValue().toString());
		} else {
			int statusCode = HttpStatusCode.BAD_REQUEST.getStatusCode();
			throw new ODataApplicationException("Not implemented",statusCode, Locale.ROOT,String.valueOf(statusCode));
		}
	}


	/*
	 * These processor methods are not handled in Auxip service
	 */
	@Override
	public void createMediaEntity(ODataRequest request, ODataResponse response, UriInfo uriInfo,
			ContentType requestFormat, ContentType responseFormat)
					throws ODataApplicationException, DeserializerException, SerializerException {
		// Check the client access role 
		if ( !AccessControl.userCanDealWith(request, uriInfo) )
		{
			int statusCode = HttpStatusCode.UNAUTHORIZED.getStatusCode();
			throw new ODataApplicationException("Unauthorized Request !",statusCode, Locale.ROOT,String.valueOf(statusCode));
		}		
		final UriResource firstResoucePart = uriInfo.getUriResourceParts().get(0);
		UriResourceEntitySet uriResourceEntitySet = (UriResourceEntitySet) firstResoucePart;
		EdmEntitySet edmEntitySet = uriResourceEntitySet.getEntitySet();
		final byte[] mediaContent = odata.createFixedFormatDeserializer().binary(request.getBody());

		final Entity entity = storage.createMediaEntity(edmEntitySet.getEntityType(), 
				requestFormat.toContentTypeString(), 
				mediaContent);
		LOG.debug("Entity created : "+entity.getType());
		//Check subscriptions
		final String uuid = entity.getProperty("Id").getValue().toString();
		LOG.debug("Incoming uuid : "+uuid);
		List<Subscription> subscriptions = storage.getAllValidSubscriptions();
		for (Subscription scr : subscriptions) {
			String filter = scr.getFilterParam();
			LOG.debug("Filter: "+filter);
			try {
				UriInfo ur = new Parser(this.serviceMetadata.getEdm(), odata).parseUri("/Products", filter, null, null);
				UriResourceEntitySet uri_ress = (UriResourceEntitySet) ur.getUriResourceParts().get(0);
				EdmEntitySet edm_set = uri_ress.getEntitySet();
				EntityCollection coll = storage.readEntitySetData(edm_set, ur.getFilterOption(), ur.getExpandOption(), 
						ur.getOrderByOption(), ur.getSkipOption(), ur.getTopOption());
				LOG.debug("Number of product subscription : "+String.valueOf(coll.getEntities().size()));
				for (Entity ent : coll.getEntities()) {
					LOG.debug("Product uuid : "+ent.getProperty("Id").getValue().toString());
					if (ent.getProperty("Id").getValue().toString().equals(uuid)) {
						LOG.debug("Matching product for subscription found");
						Notification notif = new Notification(ent.getProperty("Name").getValue().toString()
								, UUID.fromString(uuid), scr);
						notif.send();
					}
				}
			} catch (UriParserException e) {
				e.printStackTrace();
			} catch (UriValidationException e) {
				e.printStackTrace();
			}
		}

		final ContextURL contextUrl = ContextURL.with().entitySet(edmEntitySet).suffix(Suffix.ENTITY).build();
		final EntitySerializerOptions opts = EntitySerializerOptions.with().contextURL(contextUrl).build();
		final SerializerResult serializerResult = odata.createSerializer(responseFormat).entity(serviceMetadata,
				edmEntitySet.getEntityType(), entity, opts);

		final String location = request.getRawBaseUri() + '/'
				+ odata.createUriHelper().buildCanonicalURL(edmEntitySet, entity);
		response.setContent(serializerResult.getContent());
		response.setStatusCode(HttpStatusCode.CREATED.getStatusCode());
		response.setHeader(HttpHeader.LOCATION, location);
		response.setHeader(HttpHeader.CONTENT_TYPE, responseFormat.toContentTypeString());		
	}


	/*
	 * These processor methods are not handled in Auxip service
	 */
	@Override
	public void updateMediaEntity(ODataRequest request, ODataResponse response, UriInfo uriInfo,
			ContentType requestFormat, ContentType responseFormat)
					throws ODataApplicationException, DeserializerException, SerializerException 
	{
		int statusCode = HttpStatusCode.NOT_IMPLEMENTED.getStatusCode();
		throw new ODataApplicationException("Not supported.", statusCode, Locale.ROOT,String.valueOf(statusCode));
	}
	@Override
	public void deleteMediaEntity(ODataRequest request, ODataResponse response, UriInfo uriInfo)
			throws ODataApplicationException {
				int statusCode = HttpStatusCode.NOT_IMPLEMENTED.getStatusCode();
				throw new ODataApplicationException("Not supported.", statusCode, Locale.ROOT,String.valueOf(statusCode));
	}

}
