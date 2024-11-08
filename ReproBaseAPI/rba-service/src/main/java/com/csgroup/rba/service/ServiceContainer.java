/**
 * Copyright (c) 2015 SDL Group
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
package com.csgroup.rba.service;

import com.csgroup.jpadatasource.JPADataSourceConfiguration;
import com.csgroup.rba.config.AuxFilesUpdateConfiguration;
import com.csgroup.rba.service.ServiceContainer;
import com.sdl.odata.service.ODataServiceConfiguration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.Banner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.Banner.Mode;
import org.springframework.boot.autoconfigure.EnableAutoConfiguration;
import org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration;
import org.springframework.boot.autoconfigure.jdbc.DataSourceTransactionManagerAutoConfiguration;
import org.springframework.boot.autoconfigure.orm.jpa.HibernateJpaAutoConfiguration;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * @author rdevries
 */
@Configuration
@EnableScheduling
@EnableAutoConfiguration(exclude = {HibernateJpaAutoConfiguration.class, DataSourceAutoConfiguration.class,
        DataSourceTransactionManagerAutoConfiguration.class })
@Import({
        JPADataSourceConfiguration.class,
        ODataServiceConfiguration.class,
        AuxFilesUpdateConfiguration.class
})
@ComponentScan
public class ServiceContainer {
    private static final Logger LOG = LoggerFactory.getLogger(ServiceContainer.class);

    public static void main(String[] args) {
        LOG.info("Starting Example Service Application container");

        SpringApplication springApplication = new SpringApplication(ServiceContainer.class);
        springApplication.setBannerMode(Mode.CONSOLE);
        springApplication.run(args);

        LOG.info("Example Service application container started");
    }

}
