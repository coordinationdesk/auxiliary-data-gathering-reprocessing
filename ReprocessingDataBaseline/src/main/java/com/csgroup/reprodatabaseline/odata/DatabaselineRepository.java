package com.csgroup.reprodatabaseline.odata;

import com.csgroup.reprodatabaseline.datamodels.*;
import org.apache.commons.io.FilenameUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import javax.persistence.EntityManager;
import javax.persistence.EntityManagerFactory;
import javax.persistence.Query;
import java.text.MessageFormat;
import java.time.ZonedDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Component
public class DatabaselineRepository {
    private static final Logger LOG = LoggerFactory.getLogger(DatabaselineRepository.class);
    private final EntityManagerFactory entityManagerFactory;
    // for internal use
    private final Map<String, Map<String, AuxTypeDeltas>> cachedAuxTypesDeltas;
    private final Map<String, Map<String, Map<String, List<String>>>> cachedMissionAuxTypesL0Parameters;
    private final Map<String, Map<String, Long>> cachedMissionAuxTypesL0ProductAges;
    private  final Map<String, S1ICIDTimeline> icidTimelineConfiguration;
    private final Map<String, List<String>> cachedMissionIcidAuxTypes;

    public DatabaselineRepository(EntityManagerFactory entityManager) {
        this.entityManagerFactory = entityManager;
        this.cachedAuxTypesDeltas = new HashMap<>();
        this.cachedMissionAuxTypesL0Parameters = new HashMap<>();
        this.cachedMissionAuxTypesL0ProductAges = new HashMap<>();
        this.icidTimelineConfiguration = new HashMap<>();
        this.cachedMissionIcidAuxTypes = new HashMap<>();
    }
    // TOO: should be moved to ReproBaselineEntityCollecitonProcessor, or
    // to another package related to RDB data
    public Map<String, AuxTypeDeltas> getAuxTypesDeltas(String mission) {
        // do this once for each mission , only if auxTypesDeltas is not already set
        LOG.info(">> Starting DatabaselineRepository.getAuxTypesDeltas for mission " + mission);
        if (!this.cachedAuxTypesDeltas.containsKey(mission)) {
            String queryString = "SELECT DISTINCT entity FROM com.csgroup.reprodatabaseline.datamodels.AuxTypeDeltas entity "
                    + "WHERE entity.isCurrent = true AND entity.mission = \'MISSION\' ORDER BY entity.creationDateTime ASC";
            queryString = queryString.replace("MISSION", mission);

            EntityManager entityManager = entityManagerFactory.createEntityManager();
            Map<String, AuxTypeDeltas> auxTypesDeltas = new HashMap<>();
            List<AuxTypeDeltas> deltasList = null;
            try {
                Query query = entityManager.createQuery(queryString);
                deltasList = query.getResultList();
                for (AuxTypeDeltas deltas : deltasList) {
                    auxTypesDeltas.put(deltas.getAuxType(), deltas);
                }
            } finally {
                entityManager.close();
            }
            LOG.info("<< Caching AuxTypesDeltas");
            this.cachedAuxTypesDeltas.put(mission, auxTypesDeltas);
        }
        LOG.info("<< Ending DatabaselineRepository.getAuxTypesDeltas");
        return this.cachedAuxTypesDeltas.get(mission);
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
    public List<L0Product> getLevel0Products(String start, String stop, String mission, String unit, String productType)
    {
        final String satellite = mission.substring(0, 2);
        final String instrument = mission.substring(2, 4);

        String queryString = "";
        if(mission.contains("S3"))
        {
            String startsWith = satellite + unit + "_" + instrument + "_0_";
            // TODO Use a table!!!
/*
            switch (instrument) {
                case "OL":
                case "SY":
                    startsWith += "EFR";
                case "SL":
                    startsWith += "SLT";
                case "MW":
                    startsWith += "MWR";
                default:
                    if( productType.contains("CAL")) startsWith += "CAL";
                    else startsWith += "SRA";
            }
*/
            if( instrument.equals("OL") || instrument.equals("SY") ) startsWith += "EFR";
            else if( instrument.equals("SL")) startsWith += "SLT";
            else if( instrument.equals("MW")) startsWith += "MWR";
            else { //SR
                if( productType.contains("CAL")) startsWith += "CAL";
                else startsWith += "SRA";
            }

            queryString = "SELECT DISTINCT entity FROM com.csgroup.reprodatabaseline.datamodels.L0Product entity "
                    + "WHERE entity.validityStart >= \'start\' AND  entity.validityStop <= \'stop\'"
                    + "AND entity.name LIKE \'literal%\'";
            queryString = queryString.replace("start", start).replace("stop", stop).replace("literal", startsWith);
        }else
        {
            String startsWith = satellite + unit;
            // for S1 and S2 we dont care about the product type
            queryString = "SELECT DISTINCT entity FROM com.csgroup.reprodatabaseline.datamodels.L0Product entity "
                    + "WHERE entity.validityStart >= 'start' AND  entity.validityStop <= 'stop'"
                    + "AND entity.name LIKE 'literal%'";
            queryString = queryString.replace("start", start).replace("stop", stop).replace("literal", startsWith);
        }

        // LOG.debug(">> queryString " + queryString);

        EntityManager entityManager = entityManagerFactory.createEntityManager();
        List<L0Product> l0_products;
        try {
            Query query_m1 = entityManager.createQuery(queryString);
            l0_products = query_m1.getResultList();
            LOG.debug("Number of level0 products found : "+String.valueOf(l0_products.size()));
        } finally {
            entityManager.close();
        }
        return l0_products;
    }
    // TODO: move to RerpoBaselineENityCollecitonProcessor
    public List<L0Product> getLevel0ProductsByName(String level0Name) {

        String reformattedLevel0Name = level0Name.replace("\\\"", "");
        reformattedLevel0Name = FilenameUtils.removeExtension(reformattedLevel0Name);

        String queryString = "SELECT DISTINCT entity FROM com.csgroup.reprodatabaseline.datamodels.L0Product entity "
                + "WHERE entity.name LIKE \'%level0Name%\'";

        queryString = queryString.replace("level0Name", reformattedLevel0Name);

        EntityManager entityManager = entityManagerFactory.createEntityManager();
        List<L0Product> l0_products;
        try {
            Query query = entityManager.createQuery(queryString);
            l0_products = query.getResultList();
            LOG.debug(MessageFormat.format("{0} L0 products match \"{1}\" in the database.", String.valueOf(l0_products.size()), reformattedLevel0Name));
        } finally {
            entityManager.close();
        }

        return l0_products;
    }

    public List<String> getIcidAuxTypes(String mission) {
        LOG.info(">> Starting DatabaselineRepository.getIcidAuxTypes");
// Get from cache lsit for the imssion
        // load from repostiory if not avaialble
        // if no aux types for th emission, set an empty list
        if (cachedMissionIcidAuxTypes.isEmpty() ) {
            // TODO: Ensure that the list is ordered
            List<String> missionIcidAuxTypes = this.loadIcidAuxTypes(mission);
            cachedMissionIcidAuxTypes.put(mission, missionIcidAuxTypes);
        }
        LOG.info(">> Ending DatabaselineRepository.getIcidAuxTypes");
        return cachedMissionIcidAuxTypes.get(mission);
    }

    public List<String> loadIcidAuxTypes(String mission) {
        String queryString = "SELECT entity FROM com.csgroup.reprodatabaseline.datamodels.ICIDAuxType entity "
                + " WHERE entity.mission = \'MISSION\' ORDER BY entity.auxType ASC";
        queryString = queryString.replace("MISSION", mission);
        EntityManager entityManager = entityManagerFactory.createEntityManager();
        List<ICIDAuxType> missionIcidAuxTypes;
        try {
            Query query = entityManager.createQuery(queryString);
            missionIcidAuxTypes = query.getResultList();
            LOG.debug(MessageFormat.format("{0} configured Aux Types supporting ICID  .",
                            String.valueOf(missionIcidAuxTypes.size())));
        } finally {
            entityManager.close();
        }
        // Extract Aux Type names from result
        List<String> icidAuxTypeNames = new ArrayList<String>();
        for(ICIDAuxType auxType : missionIcidAuxTypes){
            icidAuxTypeNames.add(auxType.getAuxType());
        }
        return icidAuxTypeNames;
    }
    public S1ICIDTimeline getIcidTimelineConfiguration(String unit) {
        LOG.info(">> Starting DatabaselineRepository.getIcidTimelineConfiguration");

        if (icidTimelineConfiguration.isEmpty() ) {
            // TODO: Ensure that the list is ordered
            S1ICIDTimeline unitIcidConfiguration = this.loadIcidTimelineConfiguration(unit);
            icidTimelineConfiguration.put(unit, unitIcidConfiguration);
        }
        LOG.info(">> Ending DatabaselineRepository.getIcidTimelineConfiguration");
        return icidTimelineConfiguration.get(unit);
    }
    private S1ICIDTimeline loadIcidTimelineConfiguration(String unit) {
        String queryString = "SELECT entity FROM com.csgroup.reprodatabaseline.datamodels.S1ICIDTimelineInterval entity "
                + " WHERE entity.unit = \'UNIT\' ORDER BY entity.fromDate ASC";
        queryString = queryString.replace("UNIT", unit);

        EntityManager entityManager = entityManagerFactory.createEntityManager();
        List<S1ICIDTimelineInterval> unitIcidConfiguration;
        try {
            Query query = entityManager.createQuery(queryString);
            unitIcidConfiguration = query.getResultList();
            LOG.debug(MessageFormat.format("Loaded ICID Timelien: {0} ", unitIcidConfiguration));
        } finally {
            entityManager.close();
        }
        return new S1ICIDTimeline(unitIcidConfiguration);
    }


    private List<AuxTypeL0ProductMaxAge> getListAuxTypeL0ProductAge(String mission) {
        String queryString = "SELECT DISTINCT entity FROM com.csgroup.reprodatabaseline.datamodels.AuxTypeL0ProductMaxAge entity "
                + "WHERE entity.mission = \'MISSION\' ORDER BY entity.auxtype ASC";
        queryString = queryString.replace("MISSION", mission);

        EntityManager entityManager = entityManagerFactory.createEntityManager();
        List<AuxTypeL0ProductMaxAge> AuxTypeL0ProductMaxAges ;
        try {
            Query query = entityManager.createQuery(queryString);
            AuxTypeL0ProductMaxAges = query.getResultList();
            // Group on two levels:
            // Aux Type
            // Parameter Name

        } finally {
            entityManager.close();
        }
        return AuxTypeL0ProductMaxAges;
    }
    public Map<String, Long> getAuxTypesL0ProductAgeTable(String mission) 	{

        LOG.info(">> Starting DatabaselineRepository.getAuxTypesL0ProductAgeTable");
        // If no Mission Aux Types has been cached , or
        // if this mission AuxTypes have not been cached
        // load from Repository and save on cache
        if ( this.cachedMissionAuxTypesL0ProductAges.isEmpty() ||
                !this.cachedMissionAuxTypesL0ProductAges.containsKey(mission))
        {
            List<AuxTypeL0ProductMaxAge> auxTypeL0ProductMaxAges = getListAuxTypeL0ProductAge(mission);
            Map<String, Long> AuxTypeL0ProductAgeTable;
            // assign to last group a list of Parameter Values
            AuxTypeL0ProductAgeTable = auxTypeL0ProductMaxAges.
                    stream().
                    collect(
                            Collectors.toMap(
                                    AuxTypeL0ProductMaxAge::getAuxtype,
                                    AuxTypeL0ProductMaxAge::getMax_seconds
                                    )
                            );
            LOG.info("  Loaded Aux Types L0 Product Max Age configuration for mission "+mission);
            this.cachedMissionAuxTypesL0ProductAges.put(mission, AuxTypeL0ProductAgeTable);
        }
        LOG.info("<< Ending DatabaselineRepository.getAuxTypesL0ProductAgeTable");
        return this.cachedMissionAuxTypesL0ProductAges.get(mission);

    }

    // TODO Define an alternate getAuxTypesL0ParametersTable funciton that reads L0Parameters table from AuxTYpes list

    private List<AuxTypeL0ParameterValue> getListAuxTypeL0ParameterValues(String mission) {
        String queryString = "SELECT DISTINCT entity FROM com.csgroup.reprodatabaseline.datamodels.AuxTypeL0ParameterValue entity "
                + "WHERE entity.mission = \'MISSION\' ORDER BY entity.auxtype ASC";
        queryString = queryString.replace("MISSION", mission);

        EntityManager entityManager = entityManagerFactory.createEntityManager();
        List<AuxTypeL0ParameterValue> auxTypeL0ParameterValues ;
        try {
            Query query = entityManager.createQuery(queryString);
            auxTypeL0ParameterValues = query.getResultList();
            // Group on two levels:
            // Aux Type
            // Parameter Name
            LOG.debug(" Retrieved from Db aux Types L0 Parameters table: "+auxTypeL0ParameterValues.toString());

        } finally {
            entityManager.close();
        }
        return auxTypeL0ParameterValues;
    }

    // TODO Define an alternate getAuxTypesL0ParametersTable funciton that reads L0Parameters table from AuxTYpes list
    public Map<String, Map<String, List<String>>> getAuxTypesL0ParametersTable(String mission) 	{
        // Map<String, Map<String, List<String>>> auxTypesL0Parameters = new HashMap<>();

        // If aux types from RBA contain L0 Parameters, just collect and aggregate into a table for each
        // Loop on types; if L0ParameterValues is not empty, browse the list and add each item to a map.
        // add the map to auxTYpesL0Parameters with key the aux type longname
        // Otherwise read from Database

        LOG.info(">> Starting DatabaselineRepository.getAuxTypesL0ParametersTable");
        // If no Mission Aux Types has been cached , or
        // if this mission AuxTypes have not been cached
        // load from Repository and save on cache
        if ( this.cachedMissionAuxTypesL0Parameters.isEmpty() ||
            !this.cachedMissionAuxTypesL0Parameters.containsKey(mission))
        {
            List<AuxTypeL0ParameterValue> auxTypeL0ParameterValues = getListAuxTypeL0ParameterValues(mission);
            Map<String, Map<String, List<String>>> AuxTypeL0ParameterValueTable;
            // assign to last group a list of Parameter Values
            AuxTypeL0ParameterValueTable = auxTypeL0ParameterValues.
                    stream().
                    collect(
                            Collectors.groupingBy(
                                    AuxTypeL0ParameterValue::getAuxtype,
                                    Collectors.groupingBy(
                                            AuxTypeL0ParameterValue::getName,
                                            Collectors.mapping(AuxTypeL0ParameterValue::getValue,
                                                    Collectors.toList()
                                            )
                                    )
                            ));
            LOG.info("  Loaded Aux Types L0 Parameters configuration for mission "+mission);
            LOG.debug(" Aux Types configured: "+AuxTypeL0ParameterValueTable.toString());

            this.cachedMissionAuxTypesL0Parameters.put(mission, AuxTypeL0ParameterValueTable);
        }
        LOG.info("<< Ending DatabaselineRepository.getAuxTypesL0ParametersTable");
        return this.cachedMissionAuxTypesL0Parameters.get(mission);

    }

}
