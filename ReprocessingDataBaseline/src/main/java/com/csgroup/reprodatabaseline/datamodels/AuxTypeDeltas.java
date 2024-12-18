package com.csgroup.reprodatabaseline.datamodels;

import java.time.LocalDateTime;

import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.Id;
import javax.persistence.metamodel.SetAttribute;

import org.hibernate.annotations.CreationTimestamp;


/**
 * This structure contains the default values ​​for delta0 and delta1 to be used with selection rules 
 * For each product type to be reprocessed, default values should be fixed for all auxiliary data files needed for its reprocessing
 * with a boolean field (isCurrent) used for updating values.
 */
@Entity(name = "auxtype_deltas")
public class AuxTypeDeltas{
	@Id @GeneratedValue
	private int id;
	/**mission based auxtypes*/
	private String mission;
	// type of the auxiliary data file to be used for the reprocessing for a given mission
	private String auxType;
	// delta time to be used while applying selection rules over auxdata files
	private int delta0;
	private int delta1;
	// flag to be used for specifying the current deltas to be used 
	private boolean isCurrent;
	@CreationTimestamp
    private LocalDateTime creationDateTime;

	public String getMission() {
		return mission;
	}
	public String getAuxType() {
		return auxType;
	}
	public LocalDateTime getCreationDateTime() {
		return creationDateTime;
	}
	public int getDelta0() {
		return delta0;
	}
	public int getDelta1() {
		return delta1;
	}
	public boolean isCurrent() {
		return isCurrent;
	}
	public void setMission(String mission) {
		this.mission = mission;
	}
	public void setAuxTypeLongName(String auxTypeLongName) {
		this.auxType = auxTypeLongName;
	}

	public void setCurrent(boolean isCurrent) {
		this.isCurrent = isCurrent;
	}
	public void setDelta0(int delta0) {
		this.delta0 = delta0;
	}
	public void setDelta1(int delta1) {
		this.delta1 = delta1;
	}
	
}


