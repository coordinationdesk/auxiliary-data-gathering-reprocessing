package com.csgroup.reprodatabaseline.datamodels;

import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.Id;

@Entity(name = "icid_auxtypes")
public class ICIDAuxType {
    @Id
    @GeneratedValue
    private int id;

    public String getMission() {
        return mission;
    }

    public void setMission(String mission) {
        this.mission = mission;
    }

    public String getAuxType() {
        return auxType;
    }

    public void setAuxType(String auxType) {
        this.auxType = auxType;
    }

    /**mission based auxtypes*/
    private String mission;
    // type of the auxiliary data file to be used for the reprocessing for a given mission
    private String auxType;

}
