package com.csgroup.reprodatabaseline.http;

import java.text.MessageFormat;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import com.csgroup.reprodatabaseline.datamodels.AuxType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import com.csgroup.reprodatabaseline.config.UrlsConfiguration;
import com.csgroup.reprodatabaseline.datamodels.AuxFile;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

@Component
public class AuxipAccess {
	private static final Logger LOG = LoggerFactory.getLogger(AuxipAccess.class);

	private final HttpHandler httpHandler;

	private final UrlsConfiguration config;

	public AuxipAccess(HttpHandler handler, UrlsConfiguration conf) {
		this.httpHandler = handler;
		this.config = conf;
	}

	public List<String> getAuxFilesWithICID(final String mission, final AuxType  auxType,
											final String ICID,
											String bearerToken) throws Exception {
		List<String> auxFileNames = new ArrayList<String>();
		final String icidAttributeName = "InstrumentConfigurationID";

		ObjectMapper mapper = new ObjectMapper();
		LOG.debug("getAuxFilesWithICID: Building GET REequest for S1 ICID: " + ICID);
		String baseUrl = config.getAuxip_url() + "/Products";
		String filterParam =String.format("$filter=startswith(Name,'%s') and contains(Name,'%s') " +
				"and Attributes/OData.CSC.StringAttribute/any(att:att/Name eq '%s' " +
				"and att/OData.CSC.StringAttribute/Value eq '%s')",
				mission, auxType.ShortName.trim(), icidAttributeName, ICID);
		String selectParam = "select=Name";
		String request = String.format("%s?%s&%s", baseUrl, filterParam,selectParam);
		LOG.debug("Sending to Auxip request: "+request);
		String getResult = httpHandler.getPost(
				request,
				bearerToken);

		JsonNode currentObj;

		try {
			currentObj = mapper.readTree(getResult.replaceAll("@", ""));
		} catch (JsonMappingException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			throw new Exception("Malformed json response");
		} catch (JsonProcessingException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			throw new Exception("Malformed json response");
		}
		JsonNode valueNode = currentObj.get("value");
		for (JsonNode value : valueNode) {
			/*
			 * {"@odata.context":"$metadata#Products(Id,Name)",
			 * "value":[{"@odata.mediaContentType":"application/json",
			 * "Id": "ffc183a9-7555-4427-b246-176e2485abed",
			 * "Name":
			 * "S2B_OPER_GIP_G2PARA_MPC__20170206T103032_V20170101T000000_21000101T000000_B00.TGZ"
			 * }
			 */
			auxFileNames.add(value.get("Name").asText());
		}
		LOG.debug("Retrieved "+ auxFileNames.size() + " " + auxType.ShortName + " files with ICID " + ICID);
		return auxFileNames;
	}

	public List<String> getListOfAuxFileURLs(final List<AuxFile> files, String bearerToken) throws Exception {
		List<String> res = new ArrayList<String>();
		ObjectMapper mapper = new ObjectMapper();
		for (AuxFile f : files) {
			LOG.debug("getListOfAuxFileeURLS: Building POST REequest for aux file " + f.FullName.trim());
			String post = httpHandler.getPost(
					config.getAuxip_url() + "/Products?$filter=contains(Name,'" + f.FullName.trim() + "\')",
					bearerToken);
			JsonNode currentObj;
			try {
				currentObj = mapper.readTree(post.replaceAll("@", ""));
			} catch (JsonMappingException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
				throw new Exception("Malformed json response");
			} catch (JsonProcessingException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
				throw new Exception("Malformed json response");
			}
			JsonNode valueNode = currentObj.get("value");
			if (valueNode.isArray()) {
				if (valueNode.size() != 1) {
					throw new Exception("Not the correct number of element returned");
				}
				for (JsonNode value : valueNode) {
					/*
					 * {"@odata.context":"$metadata#Products",
					 * "value":[{"@odata.mediaContentType":"application/json","Id":
					 * "ffc183a9-7555-4427-b246-176e2485abed", "Name":
					 * "S2B_OPER_GIP_G2PARA_MPC__20170206T103032_V20170101T000000_21000101T000000_B00.TGZ",
					 * "ContentType":"application/octet-stream","ContentLength":3039,
					 * "OriginDate":"2017-02-06T09:30:32Z","PublicationDate":
					 * "2021-03-12T10:26:33.658341Z", "EvictionDate":"2123-08-27T09:26:33.658323Z",
					 * "Checksum":[{"ChecksumDate":"2021-03-12T10:26:33.658341Z","Algorithm":"md5",
					 * "Value":"551bb28d4f81a94e866369fa49f89760"}],
					 * "ContentDate":{"Start":"2016-12-31T23:00:00Z","End":"2099-12-31T23:00:00Z"}}]
					 * }
					 */
					UUID id = UUID.fromString(value.get("Id").asText());

					// String post_wasabi = httpHandler.getLocation(config.getAuxip_url()+
					// "/Products("+id.toString()+")/$value", bearerToken);

					String auxipLink = config.getExternalAuxip_url() + "/Products(" + id.toString() + ")/$value";

					res.add(auxipLink);
				}
			}
		}
		return res;
	}

	public void setAuxFileUrls(List<AuxFile> files, String bearerToken)
			throws Exception {
		ObjectMapper mapper = new ObjectMapper();
		for (AuxFile f : files) {
			if (f.AuxipUrl == null) {
				LOG.debug("setListOfAuxFileeURLS: Building POST REequest for aux file " + f.FullName.trim());
				String post = httpHandler.getPost(
						config.getAuxip_url() + "/Products?$filter=contains(Name,'" + f.FullName.trim() + "\')",
						bearerToken);
				JsonNode currentObj;
				try {
					currentObj = mapper.readTree(post.replaceAll("@", ""));
				} catch (JsonMappingException e) {
					e.printStackTrace();
					throw new Exception("Malformed json response");
				} catch (JsonProcessingException e) {
					e.printStackTrace();
					throw new Exception("Malformed json response");
				}
				JsonNode valueNode = currentObj.get("value");
				if (valueNode.isArray()) {
					if (valueNode.size() != 1) {
						throw new Exception("Not the correct number of element returned");
					}
					for (JsonNode value : valueNode) {
						/*
						 * {"@odata.context":"$metadata#Products",
						 * "value":[{"@odata.mediaContentType":"application/json","Id":
						 * "ffc183a9-7555-4427-b246-176e2485abed", "Name":
						 * "S2B_OPER_GIP_G2PARA_MPC__20170206T103032_V20170101T000000_21000101T000000_B00.TGZ",
						 * "ContentType":"application/octet-stream","ContentLength":3039,
						 * "OriginDate":"2017-02-06T09:30:32Z","PublicationDate":
						 * "2021-03-12T10:26:33.658341Z", "EvictionDate":"2123-08-27T09:26:33.658323Z",
						 * "Checksum":[{"ChecksumDate":"2021-03-12T10:26:33.658341Z","Algorithm":"md5",
						 * "Value":"551bb28d4f81a94e866369fa49f89760"}],
						 * "ContentDate":{"Start":"2016-12-31T23:00:00Z","End":"2099-12-31T23:00:00Z"}}]
						 * }
						 */
						UUID id = UUID.fromString(value.get("Id").asText());

						// String post_wasabi = httpHandler.getLocation(config.getAuxip_url()+
						// "/Products("+id.toString()+")/$value", bearerToken);

						String auxipLink = config.getExternalAuxip_url() + "/Products(" + id.toString() + ")/$value";
						f.AuxipUrl = auxipLink;
					}
				}
			}

		}
		// return res;
	}
}
