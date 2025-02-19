package com.csgroup.reprodatabaseline.datamodels;

import com.csgroup.reprodatabaseline.config.L0NameAttributesConfiguration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Map;

//@Component
public class L0NameParser {
    private static final Logger LOG = LoggerFactory.getLogger(L0NameParser.class);
    // Configuration tparse attributes from L0 Name (TODO: move to L0Product)
    //@Autowired
    private static L0NameAttributesConfiguration L0ParametersConfiguration;

    public static void setL0ParametersConfiguration(L0NameAttributesConfiguration l0ParametersConfiguration) {
        L0ParametersConfiguration = l0ParametersConfiguration;
    }

    final private Map<String, L0NameAttributesConfiguration.SubStringConfig> missionParametersConfiguration;

    public L0NameParser(String mission) {
        this.L0ParametersConfiguration = new L0NameAttributesConfiguration();
        LOG.debug("L0 Name Parser for mission "+mission);
        this.missionParametersConfiguration = L0ParametersConfiguration.getMissionL0NameAttributesConfig(mission);
    }

    private String parseL0Attribute(String l0ProductName,
                                    L0NameAttributesConfiguration.SubStringConfig attributeConfig) {
        int start = attributeConfig.getStartPos();
        int end = start + attributeConfig.getNumChars();
        return l0ProductName.substring(start, end);

    }
    /**
     *
     * @param l0ProductName
     * @param parameterName
     * @return
     * @throws Exception
     */
    public String getL0ParameterValue(String l0ProductName, String mission,
                                      String parameterName) throws Exception {
        L0NameAttributesConfiguration.SubStringConfig  L0AttributeConfiguration;
        L0AttributeConfiguration = L0ParametersConfiguration.getL0NameAttributeConfig(mission,
                parameterName);
        return parseL0Attribute(l0ProductName, L0AttributeConfiguration);
    }

    /**
     *
     * @param l0ProductName
     * @param parameterName
     * @return
     * @throws Exception
     */
    public String getL0ParameterValue(String l0ProductName, String parameterName) throws Exception {
        L0NameAttributesConfiguration.SubStringConfig  L0AttributeConfiguration;
        L0AttributeConfiguration = missionParametersConfiguration.get(parameterName);
        return parseL0Attribute(l0ProductName, L0AttributeConfiguration);
    }
}
