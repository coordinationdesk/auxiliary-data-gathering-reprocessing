package com.csgroup.reprodatabaseline.l0parameterauxtypes;

import com.csgroup.reprodatabaseline.datamodels.L0NameParser;
import com.csgroup.reprodatabaseline.datamodels.L0Product;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class L0NameParserTest {

    @Test
    void S1ModeParameterParse() {
        L0NameParser s1l0parser = new L0NameParser("S1SAR");
        L0Product l0IWProduct = new L0Product();
        l0IWProduct.setName("S1A_IW_RAW__0NDV_20201001T062556_20201001T063833_034599_040733_8B28.SAFE.zip");
        assertDoesNotThrow(() -> s1l0parser.getL0ParameterValue(l0IWProduct.getName(),
                "Mode"));
        try {
            assertEquals("IW", s1l0parser.getL0ParameterValue(l0IWProduct.getName(),
                    "Mode"));
        }
        catch (Exception ex) {

        }
    }
    @Test
    void S1PolarizationParameterParse() {
        L0NameParser s1l0parser = new L0NameParser("S1SAR");
        L0Product l0IWProduct = new L0Product();
        l0IWProduct.setName("S1A_IW_RAW__0NDV_20201001T062556_20201001T063833_034599_040733_8B28.SAFE.zip");
        assertDoesNotThrow(() -> s1l0parser.getL0ParameterValue(l0IWProduct.getName(),
                "Polarization"));
        try {
            assertEquals("V", s1l0parser.getL0ParameterValue(l0IWProduct.getName(),
                    "Polarization"));
        }
        catch (Exception ex) {

        }
    }
}