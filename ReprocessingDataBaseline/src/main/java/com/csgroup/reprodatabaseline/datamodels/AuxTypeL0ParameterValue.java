/**
 * Copyright (c) 2024 Telespazio
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.csgroup.reprodatabaseline.datamodels;

import javax.persistence.*;

/**
 * THis entity specifies for an Aux Type a L0 attribute value
 * that must be present in the L0 product to be processed,
 * to allow selection of AuxFiles for that AuxTYpe
 *
 * The same attribute could be specified with multiple values
 * by repeating it for each value
 *
 */
@Entity(name = "auxtype_l0parametervalues")
public class AuxTypeL0ParameterValue {
    @Id
    @GeneratedValue(strategy= GenerationType.IDENTITY)
    private int id;

    @Column(name="auxtype")
    private String auxtype;

    private String name;

    private String value;
    private String mission;

    public String getAuxtype() {
        return auxtype;
    }
    public void setAuxtype(String auxtype) {
        this.auxtype = auxtype;
    }

    public String getName() {
        return name;
    }
    public void setName(String name) {
        this.name = name;
    }

    public String getValue() {
        return value;
    }
    public void setValue(String value) {
        this.value = value;
    }

    public String getMission() {
        return mission;
    }
    public void setMission(String mission) {
        this.mission = mission;
    }

}
