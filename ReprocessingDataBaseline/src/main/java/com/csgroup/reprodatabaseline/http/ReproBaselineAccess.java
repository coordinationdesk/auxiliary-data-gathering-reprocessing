package com.csgroup.reprodatabaseline.http;

import java.text.MessageFormat;
import java.time.Duration;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import com.csgroup.reprodatabaseline.datamodels.*;
import com.csgroup.reprodatabaseline.odata.DatabaselineRepository;
import org.apache.commons.io.FilenameUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import com.csgroup.reprodatabaseline.config.UrlsConfiguration;
//import com.csgroup.reprodatabaseline.rules.RuleApplierFactory;
//import com.csgroup.reprodatabaseline.rules.RuleApplierInterface;
//import com.csgroup.reprodatabaseline.rules.RuleEnum;
import org.springframework.transaction.TransactionUsageException;

@Component
public class ReproBaselineAccess {
	private static final Logger LOG = LoggerFactory.getLogger(ReproBaselineAccess.class);

	private final HttpHandler httpHandler;
	private final UrlsConfiguration config;
	// private final AuxipAccess auxip;

	// for internal use
	private String accessToken;
	// ReproBaselineAccess entity can be used several times for the same productType
	// so for the performences optimization and to avoid requesting for the same data , AuxTypes and AuxFiles should be keeped in memory
	private final Map<String,AuxTypes> cachedAuxTypes;
	private final Map<String,List<AuxFile>> cachedAuxFiles;
	//private final DatabaselineRepository baselineRepository;

	public String getAccessToken() {
		return accessToken;
	}

	public void setAccessToken(String accessToken) {
		this.accessToken = accessToken;
	}

	public ReproBaselineAccess(HttpHandler handler, UrlsConfiguration conf) {
		this.httpHandler = handler;
		this.config = conf;
		//this.auxip = auip;

		this.cachedAuxFiles = new HashMap<>();
		this.cachedAuxTypes = new HashMap<>();
		//this.cachedAuxTypesDeltas = new HashMap<>();

		// this.baselineRepository = dataRepository;
	}

	// TODO make it protected or private
	private AuxTypes getListOfAuxTypes(final String mission){
		LOG.info(">> Starting ReproBaselineAccess.getListOfAuxTypes");

		String res = httpHandler.getPost(config.getReprocessing_baseline_url()+
				"/AuxTypes?$expand=ProductTypes&$filter=Mission eq \'"+
				mission+"\'",this.accessToken);
		AuxTypes res_aux = AuxTypes.loadValues(res);

		if(mission.contains("S3"))
		{
			// add S3ALL types
			String s3All = httpHandler.getPost(config.getReprocessing_baseline_url()+
			"/AuxTypes?$expand=ProductTypes&$filter=Mission eq \'S3ALL\'",this.accessToken);
			res_aux.add(AuxTypes.loadValues(s3All).getValues());
		}

		LOG.info(String.valueOf(res_aux.getValues().size()));
		LOG.info("<< Ending ReproBaselineAccess.getListOfAuxTypes");

		return res_aux;
	}
	// TODO make it protetcd or private
	public List<AuxFile> getListOfAuxFiles(final AuxType type, final String sat, final String unit){
		LOG.info(">> Starting ReproBaselineAccess.getListOfAuxFiles");

		// TODO Move to AuxTYpe : getLongNameNormalized
		// remove _S1 and _S2 from AUX_RESORB_S1,AUX_PREORB_S2,AUX_PREORB_S1,AUX_RESORB_S2,AUX_POEORB_S1 )
		String longName = type.LongName;
		if(longName.contains("AUX_RESORB") || longName.contains("AUX_PREORB") || longName.contains("AUX_POEORB") )
		{
			longName = longName.split("_S")[0];
		}
		//Maybe it-s shortName on type ?
		// Retrieve Aux files both for Mission + Unit (A/B/C) and for Mission generic (i.e.: S1_)
		String res = httpHandler.getPost(config.getReprocessing_baseline_url()+
				"/AuxFiles?$expand=AuxType&$filter=startswith(FullName,\'"+sat+
				"_\') and contains(FullName,\'"+longName+"\')",this.accessToken);
		List<AuxFile> res_aux = AuxFile.loadValues(type,res);
		res = httpHandler.getPost(config.getReprocessing_baseline_url()+
				"/AuxFiles?$expand=AuxType&$filter=startswith(FullName,\'"+sat+unit+
				"\') and contains(FullName,\'"+longName+"\')",this.accessToken);
		List<AuxFile> res_aux_unit = AuxFile.loadValues(type,res);
		res_aux.addAll(res_aux_unit);
		LOG.info(String.valueOf(res_aux.size()));
		LOG.info("<< Ending ReproBaselineAccess.getListOfAuxFiles");

		return res_aux;
	}

	public List<AuxFile> getAuxFiles(final AuxType auxType, final String mission, final String unit) 	{
		String key = auxType.LongName + mission + unit ;
		if( ! this.cachedAuxFiles.containsKey(key))
		{
			this.cachedAuxFiles.put(key,
					getListOfAuxFiles(auxType, mission, unit));
		}
		return this.cachedAuxFiles.get(key);
	}


	// TODO: Modify to use a Table/Map
	public String getMission(String platformShortName,String productType) 	{
		if( platformShortName.equals("S3"))
		{
			if( productType.contains("OL"))
			{
				return "S3OLCI";
			}
			if( productType.contains("SL"))
			{
				return "S3SLSTR";
			}
			if( productType.contains("SY"))
			{
				return "S3SYN";
			}
			if( productType.contains("SR"))
			{
				return "S3SRAL";
			}
			if( productType.contains("MW"))
			{
				return "S3MWR";
			}
		}else if(platformShortName.equals("S2"))
		{
			return "S2MSI";
		}else{ // S1 
			return "S1SAR";
		}

		return null;
	}

	public AuxTypes getAuxTypes(String mission) {
		// TODO: This is a ReproBaseLineAccess method : getAuxTypes(Mission)
		if( !this.cachedAuxTypes.containsKey(mission) )
		{
			AuxTypes types = getListOfAuxTypes(mission);
			this.cachedAuxTypes.put(mission, types);
		}
		return this.cachedAuxTypes.get(mission);
	}


}
