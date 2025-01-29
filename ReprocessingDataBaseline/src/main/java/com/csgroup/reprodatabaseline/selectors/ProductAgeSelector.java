package com.csgroup.reprodatabaseline.selectors;

import com.csgroup.reprodatabaseline.datamodels.AuxFile;
import com.csgroup.reprodatabaseline.datamodels.L0Product;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import static java.time.temporal.ChronoUnit.DAYS;

public class ProductAgeSelector {
    private static final Logger LOG = LoggerFactory.getLogger(AuxTypeL0Selector.class);
    private final L0Product l0Product;
    private final Map<String, Long> auxTypesMaxAges;


    public ProductAgeSelector(L0Product l0Product,
                              Map<String, Long> maxAgesConfiguration) {
        this.l0Product = l0Product;
        this.auxTypesMaxAges = maxAgesConfiguration;
    }

    /**
     * This method select the specified AuxFIle based
     * on L0 Product distance w.r.t. the Aux File
     * If a product Age configuration is defined for
     * the Aux File Aux Type, and the distance in days
     * between the AuxFile start Validity and the L0 Product
     * start validity is greater than the max age value
     * the file is not selected
     * @param auxFile The AUxFile to be checked against L0 Product
     * @return Boolean: True if selected, False otherwise
     * @throws Exception
     */
    public Boolean selectAuxFile(final AuxFile auxFile) throws Exception {
        LOG.debug(">> Starting check of AuxFile vs L0 Product time distance  ");
        // Check if aux Type has associated any L0 Parameter
        Boolean selected = Boolean.TRUE;
        if (auxTypesMaxAges.containsKey(auxFile.AuxType)) {
            LOG.debug(String.format(">>> AuxType %s has configured a max time distance w.r.t L0", auxFile.AuxType));
            Long maxDays = auxTypesMaxAges.get(auxFile.AuxType);

            // long diffTime = l0Product.getValidityStart(). - auxFile.ValidityStart.toEpochSecond();
            // long auxFileVsL0NumDays = diffTime / (1000 * 60 * 60 * 24);
            // long auxFileVsL0NumDays = l0Product.getValidityStart().until(auxFile.ValidityStart);
            long auxFileVsL0NumDays = DAYS.between(l0Product.getValidityStop(), auxFile.ValidityStop);
            selected = auxFileVsL0NumDays < 0 || auxFileVsL0NumDays < maxDays;
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
