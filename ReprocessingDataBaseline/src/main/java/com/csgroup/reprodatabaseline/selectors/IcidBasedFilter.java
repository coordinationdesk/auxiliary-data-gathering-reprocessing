package com.csgroup.reprodatabaseline.selectors;

import com.csgroup.reprodatabaseline.datamodels.AuxFile;
import com.csgroup.reprodatabaseline.datamodels.L0Product;
import com.csgroup.reprodatabaseline.datamodels.S1ICIDTimeline;
import com.csgroup.reprodatabaseline.odata.ReproDataBaseline;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.text.MessageFormat;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.ZonedDateTime;
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
     * @throws Exception
     */
    public IcidBasedFilter(S1ICIDTimeline icidConfiguration,
                           L0Product l0product,
                           String platformShortName) throws Exception
    {
        ZonedDateTime validityStart = l0product.getLevel0StartStop(platformShortName)._t0;
        String icid = l0product.getIcid(); 
        if (icid == null) {
            icid = String.valueOf(icidConfiguration.getIcid(validityStart));
            LOG.debug(MessageFormat.format(">> No ICID Value for L0  {0}: taking value from Timeline configuration",
                    l0product.getName()));
        }
        this.l0Icid = icid;
        LOG.debug(MessageFormat.format(">> Instantiated ICD Filter for Aux Files: ICID at time {0}: {1}",
                validityStart, this.l0Icid));
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
