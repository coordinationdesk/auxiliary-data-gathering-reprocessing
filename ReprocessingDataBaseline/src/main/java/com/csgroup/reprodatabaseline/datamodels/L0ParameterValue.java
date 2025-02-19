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

// TODO: Consider defining instead as a Pair<String, String>
// One single value for a L0 Parameter, asssociated with
// An AuxTYpe
// To be retrieve expanding AuxTYpe retrieved from RBA
public class L0ParameterValue {

    private String Name;

    private String Value;

    public String getName() {
        return Name;
    }

    public void setName(String name) {
        Name = name;
    }

    public String getValue() {
        return Value;
    }

    public void setValue(String value) {
        Value = value;
    }
}
