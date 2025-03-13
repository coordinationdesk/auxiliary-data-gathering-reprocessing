package com.csgroup.reprodatabaseline.selectors;

import com.csgroup.reprodatabaseline.datamodels.AuxFile;
import com.csgroup.reprodatabaseline.datamodels.L0Product;
import com.csgroup.reprodatabaseline.rules.RuleUtilities;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

//import java.time.LocalDateTime;
import java.time.ZonedDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import static java.time.temporal.ChronoUnit.DAYS;
import static java.time.temporal.ChronoUnit.SECONDS;

public class ProductAgeSelector {
    private static final Logger LOG = LoggerFactory.getLogger(ProductAgeSelector.class);
    // private final L0Product l0Product;
    private final Map<String, Long> auxTypesMaxAges;
    private final L0Product.T0T1DateTime l0Interval;



    /**
     * The class is in charge of Selecting Aux Files based on their
     * age (validity time distance) w.r.t. the L0 Product to be
     * processed
     *
     * @param l0interval The Start/Stop interval of the L0 Product to be processed
     * @param maxAgesConfiguration A table with the Aux Types max age vs L0 Product
     */
    public ProductAgeSelector(L0Product.T0T1DateTime l0interval,
                              Map<String, Long> maxAgesConfiguration) {
        this.l0Interval = l0interval;
        this.auxTypesMaxAges = maxAgesConfiguration;
    }

    protected ZonedDateTime getL0ReferenceTime()  {
        //return this.l0Interval._t1;
        ZonedDateTime middle = RuleUtilities.getMeanTime(this.l0Interval._t0,
                                                         this.l0Interval._t1);
        return middle;
    }
    public Boolean configuredProductAgeForAuxType(String auxTypeShortName) {
        return this.auxTypesMaxAges.containsKey(auxTypeShortName);
    }

    /**
     * This method select the specified AuxFIle based
     * on L0 Product distance w.r.t. the Aux File
     * If a product Age configuration is defined for
     * the Aux File Aux Type, and the distance in seconds
     * between the AuxFile start Validity and the L0 Product
     * start validity is greater than the max age value
     * the file is not selected
     * @param auxFile The AUxFile to be checked against L0 Product
     * @return Boolean: True if selected, False otherwise
     * @throws Exception
     */
    public Boolean selectAuxFile(final AuxFile auxFile) throws Exception {
        //LOG.debug(">> Starting check of AuxFile vs L0 Product time distance  ");
        // Check if aux Type has associated any L0 Parameter
        Boolean selected = Boolean.TRUE;
        if (auxTypesMaxAges.containsKey(auxFile.AuxType)) {
            // Long maxDays = auxTypesMaxAges.get(auxFile.AuxType);
            Long maxSeconds = auxTypesMaxAges.get(auxFile.AuxType);
            LOG.debug(String.format(">>> AuxType %s has configured a max time distance w.r.t L0 of %d seconds",
                                    auxFile.AuxType, maxSeconds));

            // long diffTime = l0Product.getValidityStart(). - auxFile.ValidityStart.toEpochSecond();
            // long auxFileVsL0NumDays = diffTime / (1000 * 60 * 60 * 24);
            // long auxFileVsL0NumDays = l0Product.getValidityStart().until(auxFile.ValidityStart);
            // long auxFileVsL0NumDays = DAYS.between(this.getL0ReferenceTime(), auxFile.ValidityStop);
            long auxFileVsL0NumSeconds = SECONDS.between(auxFile.ValidityStop, this.getL0ReferenceTime());
            LOG.debug(String.format(">>> Aux File Age w.r.t. L0 is of %d seconds", auxFileVsL0NumSeconds));
            selected = auxFileVsL0NumSeconds < 0 || auxFileVsL0NumSeconds < maxSeconds;
            //selected = auxFileVsL0NumSeconds < 0 || auxFileVsL0NumSeconds < maxSeconds;
        }
        return selected;
    }

    // TODO: Check: how to manage exception:
    //    skip aux file raising exception, or skip the whole AuxTYpe?
    public List<AuxFile> filter(final List<AuxFile> repro_files) throws Exception {
        List<AuxFile> filtered_files = new ArrayList<>();
        for (AuxFile auxFile : repro_files) {
            if (selectAuxFile(auxFile)) {
                filtered_files.add(auxFile);
            }
        }
        return filtered_files;
    }
}
