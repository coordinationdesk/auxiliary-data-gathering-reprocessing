package com.csgroup.reprodatabaseline.datamodels;

import javax.persistence.*;

/**
 * The configuration for Aux TYpes
 * defining the max number of days between the
 * Aux FIles of this AuxType and the L0 Product to
 * be processed
 * The configuration is defined only for
 * Aux Types that have a max age.
 * If no max age is defined, the Aux Type has no configuration items
 */
@Entity(name = "auxtype_l0productmaxage")
public class AuxTypeL0ProductMaxAge {
    @Id
    @GeneratedValue(strategy= GenerationType.IDENTITY)
    private int id;
    @Column(name="auxtype")
    private String auxtype;

    @Column(name="mission")
    private String mission;

    /**
     * Max number of seconds between AuxFile and L0 Product
     * to use the AuxFile
     */
    @Column(name="maxage")
    private long max_seconds;

    public String getAuxtype() { return auxtype;}
    public void setAuxtype(String auxtype) { this.auxtype = auxtype;}

    public String getMission() { return mission;}

    public void setMission(String mission) { this.mission = mission;}


    public long getMax_seconds() { return max_seconds;}
    public void setMax_seconds(long maxseconds) {this.max_seconds = maxseconds;}

}
