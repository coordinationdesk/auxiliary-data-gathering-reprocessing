package com.csgroup.reprodatabaseline.odata;

import com.csgroup.reprodatabaseline.datamodels.*;
import com.csgroup.reprodatabaseline.selectors.AuxTypeL0Selector;
import com.csgroup.reprodatabaseline.http.AuxipAccess;
import com.csgroup.reprodatabaseline.http.ReproBaselineAccess;
import com.csgroup.reprodatabaseline.rules.RuleApplierFactory;
import com.csgroup.reprodatabaseline.rules.RuleApplierInterface;
import com.csgroup.reprodatabaseline.selectors.IcidBasedFilter;
import com.csgroup.reprodatabaseline.selectors.ProductAgeSelector;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.text.MessageFormat;
import java.time.Duration;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

@Component
public class ReproDataBaseline {
    private static final Logger LOG = LoggerFactory.getLogger(ReproDataBaseline.class);

    private final AuxipAccess auxip;
    private final ReproBaselineAccess reproBaselineAccess;
    private final DatabaselineRepository baselineRepository;
    private String accessToken;

    // TODO Move RDB entities to separate class/file databaselineconfiguration: auxtypes deltas, auxtypes l0 parameters,
    //        and L0 Products
    // entity manager factory is moved to that class
    // this class uses: auxip, reprobaselineAccess, databaselineconfiguration
    public ReproDataBaseline(ReproBaselineAccess reproBaselineAccess, AuxipAccess auip, DatabaselineRepository dataRepository) {
        this.reproBaselineAccess = reproBaselineAccess;
        this.auxip = auip;
        this.baselineRepository = dataRepository;
    }

    public String getAccessToken() {
        return accessToken;
    }

    public void setAccessToken(String accessToken) {
        this.accessToken = accessToken;
    }

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

    private L0Product.T0T1DateTime getLevel0StartStop(L0Product level0, String platformShortName) {
        L0Product.T0T1DateTime t0t1;
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
    private L0Product.T0T1DateTime getT0T1FromName(String prodName, int startPos, int endPos, int timeFieldLen) {
        L0Product.T0T1DateTime t0t1 = new L0Product.T0T1DateTime();
        t0t1._t0 = ZonedDateTime.parse(prodName.subSequence(startPos, startPos+timeFieldLen),DateTimeFormatter.ofPattern("yyyyMMdd'T'HHmmss").withZone(ZoneId.of("UTC")));
        t0t1._t1 = ZonedDateTime.parse(prodName.subSequence(endPos, endPos+timeFieldLen),DateTimeFormatter.ofPattern("yyyyMMdd'T'HHmmss").withZone(ZoneId.of("UTC")));

        return t0t1;
    }

    private L0Product.T0T1DateTime getT0T1ForS3(L0Product level0) {

        // We should read t0 and t1 from the validityStart and validityStop of the L0Product, but having the L0Product object is new and not
        // necessary for the following operation. To keep the current service stable, we left it the way it was since the launching of the service.

        // S3B_OL_0_EFR____20210418T201042_20210418T201242_20210418T215110_0119_051_242______LN1_O_NR_002.SEN3
        return getT0T1FromName(level0.getName(), 16, 32, 15);
    }

    // TODO: these functions are not linked to class

    private L0Product.T0T1DateTime getT0T1ForS2(L0Product level0) {

        L0Product.T0T1DateTime t0t1 = new L0Product.T0T1DateTime();

        if (level0 != null && level0.getValidityStart() != null) {
            // L0Product was found on database

            // Retrieve the t0t1 from the database content
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

    private L0Product.T0T1DateTime getT0T1ForS1(L0Product level0) {

        // We should read t0 and t1 from the validityStart and validityStop of the L0Product, but having the L0Product object is new and not
        // necessary for the following operation. To keep the current service stable, we left it the way it was since the launching of the service.

        // S1A_IW_RAW__0SDV_20201102T203348_20201102T203421_035074_0417B3_02B4.SAFE.zip
        return getT0T1FromName(level0.getName(), 17, 33, 15);
    }

    // TODO: modify to use AuxFile property Band
    // TODO: Move to AuxFile Model
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
    private Boolean auxTypeWithIcid(String mission, AuxType auxType) {
        List<String> icidAuxTypes = this.baselineRepository.getIcidAuxTypes(mission);
        if (icidAuxTypes.size() == 0) {
            return Boolean.FALSE;
        }
        return icidAuxTypes.contains(auxType.LongName);
    }
    private Boolean selectAuxType(AuxType auxType, String productType,
                                  AuxTypeL0Selector l0Selector) throws Exception
    {
        // TODO:  define  another Filter for AuxTYpe based on ProductType
        // take into account only auxiliary data files with requested product type
        // but take care about auxtype from mission S3ALL
        // In thiw way we could just apply a chain of filters:
        //   ProductTypeFilter, followed by L0ParameterFilter
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
    private List<AuxFile> selectAuxFilesByRule(List<AuxFile> reprocessingFiles,
                                               Map<String, AuxTypeDeltas> auxTypesDeltas,
                                               AuxType auxType,
                                               L0Product.T0T1DateTime l0Interval) {
        List<AuxFile> files_repro_filtered;

        if (!reprocessingFiles.isEmpty()) {
            RuleApplierInterface rule_applier = RuleApplierFactory.getRuleApplier(auxType.Rule);
            Duration delta0 = Duration.ofSeconds(auxTypesDeltas.get(auxType.LongName).getDelta0());
            Duration delta1 = Duration.ofSeconds(auxTypesDeltas.get(auxType.LongName).getDelta1());
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

    // TODO: understand if we receive the Access token, or if it is ta by reprobaseAccess
    // TODO: move all local repository related Entities retrieval methods to separate class
    public List<AuxFile> getReprocessingDataBaseline(L0Product level0,String mission,String unit,String productType) {
        // 1 -> get mission and sat_unit
        // 2 -> get AuxType for this mission
        // 3 -> get AuxFiles
        // 4 -> apply rules
        // 5 -> return the selected Auxfiles

        LOG.info(">> Starting ReproBaselineAccess.getReprocessingDataBaseline");

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
        // get deltas to be applied with selection rules for a given mission
        Map<String, AuxTypeDeltas> auxTypesDeltas = this.baselineRepository.getAuxTypesDeltas(mission);
        LOG.debug(">>> Loading Aux Types for mission");
        AuxTypes types = this.reproBaselineAccess.getAuxTypes(mission);

        LOG.debug(">>> Loading Aux Types configuration w.r.t. L0 attributes");
        // For each AuxTYpe name, define a table with : parameter Name, list of Values
        Map<String, Map<String, List<String>>> auxTypesL0Parameters = this.baselineRepository.getAuxTypesL0ParametersTable(platformShortName);
        // TODO: Use a table of positions of time fields in L0 Product name, based on mission
        L0Product.T0T1DateTime t0t1 = getLevel0StartStop(level0, platformShortName);
        //L0Product.T0T1DateTime t0t1 = level0.getLevel0StartStop(platformShortName);

        // AuxTypeSelector allows to select AuxType based on L0 attribute values
        //  L0 product is used to get its attributes
        //  aux types L0 parameters is the table specifying the association between AuxTYpes and L0Attributes
        // read from configuration
        AuxTypeL0Selector l0AuxTypeSelector = null;
        if (auxTypesL0Parameters != null) {
            LOG.debug(">>> Creating a Selector For Aux Types based on L0 Parameters");
            l0AuxTypeSelector = new AuxTypeL0Selector(level0, mission, auxTypesL0Parameters);
        }
        LOG.debug(">>> Loading Aux Types product age configuration ");
        // For some Aux Types, Aux Files that have a validity too far in the
        // past w.r.t. the L0 Product, are discarded
        Map<String, Long> maxAuxFileAges = baselineRepository.getAuxTypesL0ProductAgeTable(mission);
        //ProductAgeSelector auxFileAgeFilter = new ProductAgeSelector(level0, maxAuxFileAges);
        ProductAgeSelector auxFileAgeFilter = new ProductAgeSelector(t0t1, maxAuxFileAges);


        IcidBasedFilter auxFileIcidSelector = null;
        LOG.debug(">>> Loading L0 ICID Timeline configuration ");
        // TODO: CCheck if configuration available for current unit (mission)
        S1ICIDTimeline icidConfiguration = baselineRepository.getIcidTimelineConfiguration(unit);

        // TODO: Verify if try should be moved internally, for each AuxType
        //  Do we accept losing one AuxTYpe files, for an error, or are we
        //     throwing all the results for any error?
        try {
            if (icidConfiguration != null && !icidConfiguration.isEmpty()) {
                LOG.debug(">>> Instantiating L0 ICID Based Filter ");
                auxFileIcidSelector= new IcidBasedFilter(icidConfiguration,  t0t1._t0);
            }
            for (AuxType t: types.getValues())
            {
                // Apply a chain of checks (AuxTypeSelector)
                //  for selection on AuxType, based on:
                //         productType, mission, L0Product

                if (selectAuxType(t, productType, l0AuxTypeSelector)) {
                    // TODO: Extract method (or move to separate object):
                    //   AuxFileSelector receivies AuxType (+auxTypesDeltas?)
                    //         platformShortName, platformSerialIde
                    //       t0t1 (L0 Interval)
                    // check if auxtype is not already treated
                    LOG.debug(">>> Loading Aux Files for Aux Type "+t.ShortName);
                    List<AuxFile> files_repro;
                    // call on reproBaselineAcess: getAuxFiles(key)
                    // reprobaseline Access returns cached and
                    // loads cached if key is not present
                    files_repro = this.reproBaselineAccess.getAuxFiles(t, platformShortName, unit);
                    if (!files_repro.isEmpty()) {
                        List<AuxFile> files_repro_filtered ;
                        // Copy files_repro to files_repro_filtered
                        files_repro_filtered = new ArrayList<AuxFile>(files_repro);
                        LOG.debug(MessageFormat.format(">> Checking if Aux Type {0} is dependent on ICID", t));
                        if (auxTypeWithIcid(platformShortName, t) && auxFileIcidSelector != null) {
                            LOG.debug(MessageFormat.format(">> Filtering Aux Type {0} with ICID", t));

                            List<String> icidAuxFileNames = auxip.getAuxFilesWithICID(platformShortName, t,
                                    auxFileIcidSelector.getL0Icid(), accessToken);
                            files_repro_filtered = auxFileIcidSelector.filter(files_repro_filtered,
                                    icidAuxFileNames);
                        }
                        // TODO Check on Aux Type configuration for Produc Age
                        //  is not neededof Type in FileAge Configuration
                        if (auxFileAgeFilter.configuredProductAgeForAuxType(t.ShortName) ) {
                            // If ProductAge is Configured for AuxTYpe, Filter list using ProductAgeSelector
                            files_repro_filtered = auxFileAgeFilter.filter(files_repro_filtered);
                        }
                        /*
                        if (auxFileAttributeSelector != null) {
                            files_repro = auxFileAttributeSelector.filter(files_repro);
                        }
                         */
                        files_repro_filtered = this.selectAuxFilesByRule(files_repro_filtered, auxTypesDeltas, t, t0t1);
                        // TODO: AuxFile has Band Property with value BXX

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

}
