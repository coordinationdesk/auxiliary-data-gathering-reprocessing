/**
 * Copyright (c) 2016 All Rights Reserved by the SDL Group.
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

//Modified package to include only the datasource
package com.csgroup.jpadatasource.query;

import com.sdl.odata.api.ODataException;
import com.sdl.odata.api.ODataNotImplementedException;
import com.sdl.odata.api.edm.model.EntityDataModel;
import com.sdl.odata.api.edm.model.EntityType;
import com.sdl.odata.api.processor.query.ArithmeticCriteriaValue;
import com.sdl.odata.api.processor.query.ComparisonCriteria;
import com.sdl.odata.api.processor.query.CompositeCriteria;
import com.sdl.odata.api.processor.query.ContainsMethodCriteria;
import com.sdl.odata.api.processor.query.Criteria;
import com.sdl.odata.api.processor.query.CriteriaValue;
import com.sdl.odata.api.processor.query.EndsWithMethodCriteria;
import com.sdl.odata.api.processor.query.LiteralCriteriaValue;
import com.sdl.odata.api.processor.query.ModOperator$;
import com.sdl.odata.api.processor.query.PropertyCriteriaValue;
import com.sdl.odata.api.processor.query.StartsWithMethodCriteria;
import com.csgroup.jpadatasource.util.JPAMetadataUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


/**
 * This class builds where clause for given criteria.
 *
 * @author Renze de Vries
 */
public class JPAWhereStrategyBuilder {
    private static final Logger LOG = LoggerFactory.getLogger(JPAWhereStrategyBuilder.class);

    private static final String PREFIX_PARAM = "value";

    private final EntityDataModel entityDataModel;
    
    private final EntityType targetEntityType;

    private final JPAQueryBuilder jpaQueryBuilder;

    private int paramCount = 0;

    public JPAWhereStrategyBuilder(EntityType targetEntityType, JPAQueryBuilder jpaQueryBuilder,EntityDataModel entityDataModel) {
        this.entityDataModel = entityDataModel;
		this.targetEntityType = targetEntityType;
        this.jpaQueryBuilder = jpaQueryBuilder;
    }

    /**
     * Takes either {@link com.sdl.odata.api.processor.query.CompositeCriteria} or
     * {@link com.sdl.odata.api.processor.query.ComparisonCriteria} and builds where clause and set it
     * to JPAQueryBuilder which is passed in constructor.
     *
     * @param criteria for which where clause should build
     * @throws ODataException in case of any errors
     */
    public void build(Criteria criteria) throws ODataException {
        LOG.debug("where clause is going to build for {}", criteria);
        StringBuilder builder = new StringBuilder();
        buildFromCriteria(criteria, builder);
        jpaQueryBuilder.setWhereClause(builder.toString());
        LOG.debug("where clause built for {}", criteria);
    }

    private void buildFromCriteria(Criteria criteria, StringBuilder builder) throws ODataException {
        if (criteria instanceof CompositeCriteria) {
            buildFromCompositeCriteria((CompositeCriteria) criteria, builder);
        } else if (criteria instanceof ComparisonCriteria) {
            buildFromComparisonCriteria((ComparisonCriteria) criteria, builder);
        } else if (criteria instanceof ContainsMethodCriteria) {
            buildFromContainsCriteria((ContainsMethodCriteria) criteria, builder);
        } else if (criteria instanceof StartsWithMethodCriteria) {
                buildFromStartsWithCriteria((StartsWithMethodCriteria) criteria, builder);
        } else if (criteria instanceof EndsWithMethodCriteria) {
            buildFromEndsWithCriteria((EndsWithMethodCriteria) criteria, builder);
        } else {
            throw new ODataNotImplementedException("Unsupported criteria type: " + criteria);
        }
    }

    private void buildFromEndsWithCriteria(EndsWithMethodCriteria criteria, StringBuilder builder) throws ODataException {
    	String containes = ""; 
    	if (criteria.getStringLiteral() instanceof LiteralCriteriaValue) {
    		containes = (String) ((LiteralCriteriaValue) criteria.getStringLiteral()).value() ;
    	 } else {
    		 throw new ODataNotImplementedException("criteria for contains is not a string");
    	 }
    	builder.append("(");
        buildFromCriteriaValue(criteria.getProperty(), builder);
        builder.append(" LIKE '%").append(containes.replace("_","\\_")).append("'  ESCAPE '\\' )");
	}

	private void buildFromStartsWithCriteria(StartsWithMethodCriteria criteria, StringBuilder builder) throws ODataException {
    	String containes = ""; 
    	if (criteria.getStringLiteral() instanceof LiteralCriteriaValue) {
    		containes = (String) ((LiteralCriteriaValue) criteria.getStringLiteral()).value() ;
    	 } else {
    		 throw new ODataNotImplementedException("criteria for contains is not a string");
    	 }
    	
    	builder.append("(");
        buildFromCriteriaValue(criteria.getProperty(), builder);
        builder.append(" LIKE '").append(containes.replace("_","\\_")).append("%' ESCAPE '\\' )");
		
	}

	private void buildFromContainsCriteria(ContainsMethodCriteria criteria, StringBuilder builder) throws ODataException {		
    	String containes = ""; 
    	if (criteria.getStringLiteral() instanceof LiteralCriteriaValue) {
    		containes = (String) ((LiteralCriteriaValue) criteria.getStringLiteral()).value() ;
    	 } else {
    		 throw new ODataNotImplementedException("criteria for contains is not a string");
    	 }
    	
    	builder.append("(");
        buildFromCriteriaValue(criteria.getProperty(), builder);
        builder.append(" LIKE '%").append(containes.replace("_","\\_")).append("%' ESCAPE '\\' )");
		
	}

	private void buildFromComparisonCriteria(ComparisonCriteria criteria, StringBuilder builder) throws ODataException {
        builder.append("(");
        buildFromCriteriaValue(criteria.left(), builder);
        builder.append(' ').append(criteria.operator().toString()).append(' ');
        buildFromCriteriaValue(criteria.right(), builder);
        builder.append(")");
    }

    private void buildFromCriteriaValue(CriteriaValue value, StringBuilder builder) throws ODataException {
        if (value instanceof LiteralCriteriaValue) {
            buildFromLiteralCriteriaValue((LiteralCriteriaValue) value, builder);
        } else if (value instanceof ArithmeticCriteriaValue) {
            buildFromArithmeticCriteriaValue((ArithmeticCriteriaValue) value, builder);
        } else if (value instanceof PropertyCriteriaValue) {
            buildFromPropertyCriteriaValue((PropertyCriteriaValue) value, builder);
        } else {
            throw new ODataNotImplementedException("Unsupported criteria value type: " + value);
        }
    }

    private void buildFromLiteralCriteriaValue(LiteralCriteriaValue value, StringBuilder builder) {
        String paramName = PREFIX_PARAM + (++paramCount);
        builder.append(':').append(paramName);
        jpaQueryBuilder.addParam(paramName, value.value());
    }

    private void buildFromArithmeticCriteriaValue(ArithmeticCriteriaValue value, StringBuilder builder)
            throws ODataException {
        // The MOD operator has to be treated as a special case, because it has a different syntax in JPQL
        if (value.operator() == ModOperator$.MODULE$) {
            builder.append("MOD(");
            buildFromCriteriaValue(value.left(), builder);
            builder.append(", ");
            buildFromCriteriaValue(value.right(), builder);
            builder.append(")");
        } else {
            buildFromCriteriaValue(value.left(), builder);
            builder.append(' ').append(value.operator().toString()).append(' ');
            buildFromCriteriaValue(value.right(), builder);
        }
    }

    private void buildFromPropertyCriteriaValue(PropertyCriteriaValue value, StringBuilder builder) {
        builder.append(jpaQueryBuilder.getFromAlias());
        builder.append(".");                
        builder.append(JPAMetadataUtil.getJPAPropertyName(targetEntityType, value.propertyName(),entityDataModel));
    }

    private void buildFromCompositeCriteria(CompositeCriteria criteria, StringBuilder builder) throws ODataException {
        builder.append("(");
        buildFromCriteria(criteria.left(), builder);
        builder.append(' ').append(criteria.operator().toString()).append(' ');
        buildFromCriteria(criteria.right(), builder);
        builder.append(")");
    }

    public int getParamCount() {
        return paramCount;
    }

    public JPAWhereStrategyBuilder setParamCount(int paramCount) {
        this.paramCount = paramCount;
        return this;
    }
}
