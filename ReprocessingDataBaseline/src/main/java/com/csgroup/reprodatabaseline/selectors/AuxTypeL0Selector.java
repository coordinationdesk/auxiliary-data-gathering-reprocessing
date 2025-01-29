package com.csgroup.reprodatabaseline.selectors;

import com.csgroup.reprodatabaseline.datamodels.L0NameParser;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.csgroup.reprodatabaseline.datamodels.AuxType;
import com.csgroup.reprodatabaseline.datamodels.L0Product;

/**
 *
 */

public class AuxTypeL0Selector {
    private static final Logger LOG = LoggerFactory.getLogger(AuxTypeL0Selector.class);
    private final L0Product l0Product;
    private final Map<String, Map<String, List<String>>> auxTypesL0ParameterValuesTable;
    // Attributes of L0 Product relevant to this instance
    // They are cached each time a new attribute is requested.
    private final Map<String, String> cachedL0Parameters;

    private final L0NameParser l0nameparser;

    // TODO: Create ENum for Parameter Names
    // TODO: Extract ALL parameters from L0 Name using a L0AttributesParser

    /**
     *
     * @param l0ProductObject The L0 Product against which AuxTypes shall be matched
     * @param mission  The mission of the L0 Product
     * @param auxTypesL0ParameterValues The table with the configuration of values for L0 Attributes
     *                                  that select AuxType
     */
    public AuxTypeL0Selector(L0Product l0ProductObject, String mission,
                             Map<String, Map<String, List<String>>> auxTypesL0ParameterValues) {
        this.l0Product = l0ProductObject;
        this.auxTypesL0ParameterValuesTable = auxTypesL0ParameterValues;
        // L0 parameters for current L0 Product Object (cached between calls for different AuxType's)
        this.cachedL0Parameters = new HashMap<>();
        l0nameparser = new L0NameParser(mission);
    }
    // TODO Make a Unit Test
    // TODO: Manage exceptions

    /**
     * This method extracts the value of a parameter from the L0 Name string
     * @param l0ProductName a String with the L0 Product name
     * @param parameterName The name of the parameter/attribute to be extracted
     * @return A string with the value of the specified parameter in the provided L0 Name
     * @throws Exception
     */
    private String getL0ParameterValue(String l0ProductName,
                                       String parameterName) throws Exception {
        if (!this.cachedL0Parameters.containsValue(parameterName)) {
            String parameterValue = this.l0nameparser.getL0ParameterValue(l0ProductName,
                    parameterName);
            cachedL0Parameters.put(parameterName, parameterValue);
        }
        return cachedL0Parameters.get(parameterName);
    }

    // TODO: Make a unit Test

    /**
     * This method receives an AuxType and by matching the relevant configuration
     * against the current L0 Product, it selects the AuxType for L0 Processing
     * @param auxType An AuxType object:
     * @return Boolean: True if the AuxType is selected for the processing of the
     * current L0 Product
     * @throws Exception
     */
    public Boolean selectAuxType(final AuxType auxType) throws Exception
    {
        LOG.debug(">> Starting check against L0 Parameters Aux Type "+auxType.LongName);
        // Check if aux Type has associated any L0 Parameter
        Boolean selected = Boolean.TRUE;
        // CHeck if aux Type associated L0 Parameter have values matching the corresponding L0 Value
        if ( auxTypesL0ParameterValuesTable.containsKey(auxType.LongName)) {
            LOG.debug(String.format(">>> AuxType %s has configured L0 Parameters", auxType.LongName));
            Map<String, List<String>> auxTypeL0Parameters = auxTypesL0ParameterValuesTable.get(auxType.LongName);
            for (String parameterName: auxTypeL0Parameters.keySet()) {
                // Check if L0Product has parameter
                String L0ParamValue = getL0ParameterValue(this.l0Product.getName(), parameterName);
                LOG.debug(String.format(" Checking Parameter %s: L0 value: %s",
                        parameterName, L0ParamValue));

                // If yes, check if L0 Product parameter value is in AuxType associate list of values
                if ( ! auxTypeL0Parameters.get(parameterName).contains(L0ParamValue)){
                    // if no, not selected
                    selected = Boolean.FALSE;
                    LOG.debug(" The L0 Parameter value is NOT configured for  "+auxType.LongName);
                    break;
                }
                LOG.debug(" The L0 Parameter value is configured for  "+auxType.LongName);
                // If L0 Product has not the parameter: TBD: continue with other parameters?
                // There is ann error: S1 L0 Products always have all the parameters
            }
        }
        LOG.debug(">> Completed  check against L0 Parameters Aux Type "+auxType.LongName);
        return selected;
    }

}
