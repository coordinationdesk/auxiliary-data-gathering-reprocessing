package com.csgroup.reprodatabaseline.selectors;

import com.csgroup.reprodatabaseline.datamodels.AuxFile;
import com.csgroup.reprodatabaseline.datamodels.L0Product;
import com.csgroup.reprodatabaseline.datamodels.S1ICIDTimeline;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.text.MessageFormat;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.HashSet;
import java.util.List;
import java.util.stream.Collectors;

public class IcidBasedFilter {
    private static final Logger LOG = LoggerFactory.getLogger(IcidBasedFilter.class);

    public String getL0Icid() {
        return l0Icid;
    }

    private final String         l0Icid;


    /**
     *      * Due to simplification, ICID value is not
     *      * read from L0 Products, but is
     *      * taken from a Timeline configuration of the ICID values
     *      * The ICID value is retrieved for the L0 product time
     * @param icidConfiguration
     * @param l0Product
     * @throws Exception
     */
    public IcidBasedFilter(S1ICIDTimeline icidConfiguration, L0Product l0Product) throws Exception
    {
        LocalDateTime referenceTime = l0Product.getValidityStart();
        this.l0Icid = String.valueOf(icidConfiguration.getIcid(referenceTime.atZone(ZoneId.of("UTC"))));
        LOG.debug(MessageFormat.format(">> Instantiated ICD Filter for Aux Files: ICID for L0 {0}: {1}",
                l0Product.getName(), this.l0Icid));

    }



    // TODO: Check: how to manage exception:
    //    skip aux file raising exception, or skip the whole AuxTYpe?
    public List<AuxFile> filter(final List<AuxFile> repro_files,
                                List<String> icidAuxFileNames) throws Exception {
        final HashSet<String> icidAuxFileNamesSet = new HashSet<>(icidAuxFileNames);
        // Filter AuxFiles based on icidAuxFileNames
        return  repro_files.stream()
                .filter(auxFile -> icidAuxFileNamesSet.contains(auxFile.FullName))
                .collect(Collectors.toList());
    }
}
