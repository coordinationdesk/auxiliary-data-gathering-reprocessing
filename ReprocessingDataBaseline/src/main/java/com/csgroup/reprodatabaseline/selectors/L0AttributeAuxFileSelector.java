package com.csgroup.reprodatabaseline.selectors;

import com.csgroup.reprodatabaseline.datamodels.AuxFile;
import com.csgroup.reprodatabaseline.datamodels.L0Product;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.List;

public class L0AttributeAuxFileSelector {
    private static final Logger LOG = LoggerFactory.getLogger(AuxTypeL0Selector.class);
    private final L0Product l0Product;
    private final String attributeName;
    // ICID Static configuration
    // AUXIP access bean
    /**
     *
     * @param l0Product
     */
    public L0AttributeAuxFileSelector(L0Product l0Product, String attribute) {
        this.l0Product = l0Product;
        this.attributeName = attribute;
        // Get the attribute Value from L0
        // if not defined, get from configuration
    }

    /**
     *
     * @param auxFiles
     * @return
     */
    public List<AuxFile> filterAuxFiles(List<AuxFile> auxFiles) {
        // 1. extract from Auxip list of files with Attribute
        //     with value saved at instantitation
        // filter the List of Aux FIle by the names retrieved from Auxip
        // i.e.: keep the AuxFiles having the name in the Auxip List
        return auxFiles;
    }

}
