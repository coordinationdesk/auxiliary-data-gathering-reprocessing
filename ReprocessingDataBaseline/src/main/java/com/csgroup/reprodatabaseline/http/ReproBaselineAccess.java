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
import com.csgroup.reprodatabaseline.rules.RuleApplierFactory;
import com.csgroup.reprodatabaseline.rules.RuleApplierInterface;
import com.csgroup.reprodatabaseline.rules.RuleEnum;
import org.springframework.transaction.TransactionUsageException;

@Component
public class ReproBaselineAccess {
	private static final Logger LOG = LoggerFactory.getLogger(ReproBaselineAccess.class);

	private final HttpHandler httpHandler;
	private final UrlsConfiguration config;
	private final AuxipAccess auxip;

	// for internal use
	private String accessToken;
	// ReproBaselineAccess entity can be used several times for the same productType
	// so for the performences optimization and to avoid requesting for the same data , AuxTypes and AuxFiles should be keeped in memory
	private final Map<String,AuxTypes> cachedAuxTypes;
	private final Map<String,List<AuxFile>> cachedAuxFiles;
	private final DatabaselineRepository baselineRepository;

	public String getAccessToken() {
		return accessToken;
	}

	public void setAccessToken(String accessToken) {
		this.accessToken = accessToken;
	}

	public ReproBaselineAccess(HttpHandler handler, UrlsConfiguration conf,AuxipAccess auip,
							   DatabaselineRepository dataRepository) {
		this.httpHandler = handler;
		this.config = conf;
		this.auxip = auip;

		this.cachedAuxFiles = new HashMap<>();
		this.cachedAuxTypes = new HashMap<>();
		//this.cachedAuxTypesDeltas = new HashMap<>();

		this.baselineRepository = dataRepository;
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
	public List<AuxFile> getListOfAuxFiles(final AuxType type, final String sat, final String unit, RuleEnum rl){
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
					getListOfAuxFiles(auxType, mission, unit, auxType.Rule));
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

	// TODO: move to RerpoBaselineENityCollecitonProcessor
	// TODO: Should be : by time interal

	/**
	 *
	 * @param start start of interval where to search for L0 Products
	 * @param stop   end of interval where to search for L0 Products
	 * @param mission: String specifying mission and instrument
	 * @param unit : the platform unit (A,B,C...): the satellite of the mission
	 * @param productType : the type of product to be generated
	 * @return a list of L0Product objects, having the validity interval intersecting the input interval
	 */
	public List<L0Product> getLevel0Products(String start,String stop, String mission,String unit,String productType) 	{
		return this.baselineRepository.getLevel0Products(start, stop,
				mission, unit, productType);
	}
	// TODO: move to databaseline Repostiory
	public List<L0Product> getLevel0ProductsByName(String level0Name) {
		return this.baselineRepository.getLevel0ProductsByName(level0Name);
	}
	
	private class T0T1DateTime {
		public ZonedDateTime _t0;
		public ZonedDateTime _t1;
	}

	private List<AuxFile> selectAuxFilesByRule(List<AuxFile> reprocessingFiles,
											   Map<String, AuxTypeDeltas> auxTypesDeltas,
											   AuxType auxType,
											   T0T1DateTime l0Interval) {
		RuleApplierInterface rule_applier = RuleApplierFactory.getRuleApplier(auxType.Rule);
		Duration delta0 = Duration.ofSeconds(auxTypesDeltas.get(auxType.LongName).getDelta0());
		Duration delta1 = Duration.ofSeconds(auxTypesDeltas.get(auxType.LongName).getDelta1());

		List<AuxFile> files_repro_filtered;

		if (!reprocessingFiles.isEmpty()) {
			LOG.debug(String.format(">>> Applying Selection Rule to %d Aux Files",
					reprocessingFiles.size()));
			// TODO: Apply any extra AxuFile Selection Rule dependent on Mission:
			//       ICID Based selection for S1
			//       Product time distance vs Aux File for S1

			// TODO: AuxFile has Band Property with value BXX
			// TODO: Replace with : if (files_repro.get(0).Band.
			if (reprocessingFiles.get(0).FullName.matches(".*B..\\..*")) {
				// The type has band files

				// We need to group the files by band and apply the rule on each group
				Map<String, List<AuxFile>> sortedFilesByBand = sortFilesByBand(reprocessingFiles);

				files_repro_filtered = new ArrayList<AuxFile>();

				for (String band : sortedFilesByBand.keySet()) {
					files_repro_filtered.addAll(rule_applier.apply(sortedFilesByBand.get(band),
							l0Interval._t0, l0Interval._t1,
							delta0, delta1));
				}

			} else {
				// The type does not have band files

				// We need to apply the rule on every file at once
				files_repro_filtered = rule_applier.apply(reprocessingFiles,
						l0Interval._t0, l0Interval._t1,
						delta0, delta1);
			}
		} else {
			// Return empty array list
			files_repro_filtered = new ArrayList<>();
		}
		return files_repro_filtered;
	}

	private Boolean selectAuxType(AuxType auxType, String productType, AuxTypeL0Selector l0Selector) throws Exception
	{
		if (auxType.usedForProductType(productType)) {
			LOG.debug(String.format("AuxType %s configured for production of %s",
					auxType.LongName, productType));
			// If selected continue, else continue with next Aux Type
			// If no configuration exists, use the AuxTYpe
			if ((l0Selector != null) && !l0Selector.selectAuxType(auxType)) {
				LOG.debug(String.format("Aux Type %s not selected due to L0 parameters",
						auxType.LongName));
				return Boolean.FALSE;
			}
			return Boolean.TRUE;
		}
		return Boolean.FALSE;
	}
	public List<AuxFile> getReprocessingDataBaseline(L0Product level0,String mission,String unit,String productType) {
		// 1 -> get mission and sat_unit
		// 2 -> get AuxType for this mission
		// 3 -> get AuxFiles for each Aux Type
		// 4 -> apply rules to each AuxFile
		// 5 -> return the selected Auxfiles

		LOG.info(">> Starting ReproBaselineAccess.getReprocessingDataBaseline");
		// TODO: Get List of Additional AuxFile Filters based on mission (S1: ProductVsAuxAge)
		// the output AuxFile listing 
		List<AuxFile> results = new ArrayList<>();

		// TODO: Move platformSHortName getter to level0
		String platformShortName = level0.getName().substring(0, 2); // "S1", "S2" or "S3"
		// TODO: Move platformSerialIdentifier getter to level0
        String platformSerialIdentifier = level0.getName().substring(2, 3); //"A" or "B" or "_"

		// Check the matching between the level0 and mission/unit
		//level0.verifyPlatform(mission, unit)
		if( !platformShortName.equals(mission.substring(0, 2)) || !platformSerialIdentifier.equals(unit) )
		{
			LOG.info(">> ReproBaselineAccess.getReprocessingDataBaseline : mismatching between level0 product " + level0.getName() + " and mission/unit " + mission + "/" + unit);
			// return an empty collection
			return results;
		}
		LOG.debug(">>> Loading Aux Types Deltas configuration");
		// get deltas to be applied with selection rules for a given mission
		Map<String, AuxTypeDeltas> auxTypesDeltas = this.baselineRepository.getAuxTypesDeltas(mission);
		LOG.debug(">>> Loading Aux Types for mission");
		AuxTypes types = getAuxTypes(mission);

		LOG.debug(">>> Loading Aux Types configuration w.r.t. L0 attributes");
		// TODO for each AuxTYpe name, dfine a table with : parameter Name, list of Values
		//Map<String, Map<String, List<String>>> auxTypesL0Parameters = getAuxTypesL0ParametersTable(auxTypes.getValues();
		Map<String, Map<String, List<String>>> auxTypesL0Parameters = baselineRepository.getAuxTypesL0ParametersTable(mission);

		T0T1DateTime t0t1 = getLevel0StartStop(level0, platformShortName);

		// AuxTypeSelector allows to select AuxType based on L0 attribute values
		//  L0 product is used to get its attributes
		//  aux types L0 parameters is the table specifying the association between AuxTYpes and L0Attributes
		// read from configuration
		AuxTypeL0Selector l0AuxTypeSelector = null;
		if (auxTypesL0Parameters != null) {
			LOG.debug(">>> Creating a Selector For Aux Types based on L0 Parameters");
			l0AuxTypeSelector = new AuxTypeL0Selector(level0, mission, auxTypesL0Parameters);
		}

		try {
			for (AuxType t: types.getValues())
			{
				// T: Consider possibility of defining another Filter for AuxTYpe based on ProductType
				// take into account only auxiliary data files with requested product type
				// but take care about auxtype from mission S3ALL
				if (selectAuxType(t, productType, l0AuxTypeSelector)) {
					// TODO: Extract method (or move to separate object):
					//   AuxFileSelector receivies AuxType (+auxTypesDeltas?)
					//         platformShortName, platformSerialIde
					//       t0t1 (L0 Interval)
					// Returns ReprocessingAuxFiles
					// call on reproBaselineAcess: getAuxFiles(key)

					LOG.debug(">>> Loading Aux Files for Aux Type "+t.ShortName);
					List<AuxFile> files_repro = this.getAuxFiles(t, platformShortName, platformSerialIdentifier);
					if (! files_repro.isEmpty()) {
						List<AuxFile> files_repro_filtered;
						files_repro_filtered = this.selectAuxFilesByRule(files_repro, auxTypesDeltas, t, t0t1);

						LOG.debug(">>> Retrieving from AUXIP download URLs for selected Aux Files");
						try {
							auxip.setAuxFileUrls(files_repro_filtered, this.accessToken);
							results.addAll(files_repro_filtered);
						} catch (Exception e) {
							e.printStackTrace();
						}
					}
				}
	
			}	
		} catch (Exception e) {
			//TODO: handle exception
			e.printStackTrace();
			LOG.debug("Exception : "+e.getLocalizedMessage());
		}


		LOG.info("<< Ending ReproBaselineAccess.getReprocessingDataBaseline");

		return results;

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

	// TODO: these functions are not linked to class
	// TODO: MOVE to L0 Product
	private T0T1DateTime getLevel0StartStop(L0Product level0, String platformShortName) {
		T0T1DateTime t0t1;
		if( platformShortName.equals("S3"))
		{
			t0t1 = getT0T1ForS3(level0);

		}else if( platformShortName.equals("S2"))
		{
			t0t1 = getT0T1ForS2(level0);

		}else
		{
			t0t1 = getT0T1ForS1(level0);

		}
		return t0t1;
	}

	private T0T1DateTime getT0T1ForS3(L0Product level0) {
		
		T0T1DateTime t0t1 = new T0T1DateTime();
		
		// We should read t0 and t1 from the validityStart and validityStop of the L0Product, but having the L0Product object is new and not
		// necessary for the following operation. To keep the current service stable, we left it the way it was since the launching of the service.
		
		// S3B_OL_0_EFR____20210418T201042_20210418T201242_20210418T215110_0119_051_242______LN1_O_NR_002.SEN3
		t0t1._t0 = ZonedDateTime.parse(level0.getName().subSequence(16, 16+15),DateTimeFormatter.ofPattern("yyyyMMdd'T'HHmmss").withZone(ZoneId.of("UTC")));
		t0t1._t1 = ZonedDateTime.parse(level0.getName().subSequence(32, 32+15),DateTimeFormatter.ofPattern("yyyyMMdd'T'HHmmss").withZone(ZoneId.of("UTC")));
		
		return t0t1;
	}

	private T0T1DateTime getT0T1ForS2(L0Product level0) {
		
		T0T1DateTime t0t1 = new T0T1DateTime();
		
		if (level0 != null && level0.getValidityStart() != null) {
			// L0Product was found on data base
			
			// Retrieve the t0t1 from the data base content
			t0t1._t0 = level0.getValidityStart().atZone(ZoneId.of("UTC"));
			t0t1._t1 = level0.getValidityStop().atZone(ZoneId.of("UTC"));
			
		} else {
			// L0Product not found 

			// We read the t0t1 from the validity date contained in the file name
			
			// S2A_OPER_MSI_L0__LT_MTI__20150725T193419_S20150725T181440_N01.01
			t0t1._t0 = ZonedDateTime.parse(level0.getName().subSequence(42, 42+15),DateTimeFormatter.ofPattern("yyyyMMdd'T'HHmmss").withZone(ZoneId.of("UTC")));
			t0t1._t1 = t0t1._t0;
		}
		
		return t0t1;
	}

	private T0T1DateTime getT0T1ForS1(L0Product level0) {
		
		T0T1DateTime t0t1 = new T0T1DateTime();
		
		// We should read t0 and t1 from the validityStart and validityStop of the L0Product, but having the L0Product object is new and not
		// necessary for the following operation. To keep the current service stable, we left it the way it was since the launching of the service.
		
		// S1A_IW_RAW__0SDV_20201102T203348_20201102T203421_035074_0417B3_02B4.SAFE.zip
		t0t1._t0 = ZonedDateTime.parse(level0.getName().subSequence(17, 17+15),DateTimeFormatter.ofPattern("yyyyMMdd'T'HHmmss").withZone(ZoneId.of("UTC")));
		t0t1._t1 = ZonedDateTime.parse(level0.getName().subSequence(33, 33+15),DateTimeFormatter.ofPattern("yyyyMMdd'T'HHmmss").withZone(ZoneId.of("UTC")));
		
		return t0t1;
	}
	// TODO: modifiy to use AuxFile property Band
	// collect into a Map based on Band property not BXX
	private Map<String, List<AuxFile>> sortFilesByBand(List<AuxFile> files) {
		Map<String, List<AuxFile>> sortedFiles = new HashMap<>();
		Pattern pattern = Pattern.compile("B..\\.");
		for (AuxFile file : files) {
			Matcher matcher = pattern.matcher(file.FullName);
			if (matcher.find()) {
				String bandName = matcher.group();
				if (!sortedFiles.containsKey(bandName)) {
					sortedFiles.put(bandName, new ArrayList<AuxFile>());
				}
				sortedFiles.get(bandName).add(file);
			}
		}
		return sortedFiles;
	}

}
