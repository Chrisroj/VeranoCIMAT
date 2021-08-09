library(rugarch)
library(tidyr)
library(purrr)

#' Perform a single ARMA + GARCH 
#'
#' @param models A list with parameters of the model
#' @param time_series A vector of time series 
#'
#' @return A dataframe with model results
#' @export
#'
#' @examples
#' NULL
garch_model <- function(models, time_series) {
    # Model Specification
    modelSpec = ugarchspec(variance.model = list(model = models$model, 
                                                 garchOrder = c(models$lag_arch, models$lag_garch)),
                           mean.model = list(armaOrder = c(models$lag_ar, models$lag_ma)),
                           distribution = models$distribution)
    
    # Model Fit
    modelFit <- ugarchfit(spec = modelSpec, data = time_series)
    
    # Get Indicators AIC and BIC
    if(is.null(coef(modelFit))){
        AIC <- BIC <- NA
    } else{
        AIC <- rugarch::infocriteria(modelFit)["Akaike", ]
        BIC <- rugarch::infocriteria(modelFit)["Bayes", ]
        
        # Model String
        modelString <- paste0('ARMA(', models$lag_ar, ',', models$lag_ma, ') + ', 
                              models$model, '(', models$lag_arch, ',', models$lag_garch, ') ', models$distribution)
        # Return 
        models <- tibble(model = modelString, 
                         AIC,
                         BIC) # PUEDO AÑADIRLE MÁS COLUMNAS GG
        
        return(models)
    }
}


#' Perform ARMA + GARCH models from a grid of parameters
#'
#' @param gridmodels A data.frame of models parameters in each row
#' @param time_series A vector of time series 
#'
#' @return A list with the result of all models
#' @export
#'
#' @examples
#' NULL
garch_grid <- function(grid_models, time_series){
    # Get results of each model
    list_results <- map(list_models, function(x) garch_model(models = x, time_series = time_series))
    
    # Join the results 
    all_models <- reduce(list_results[!is.na(list_results)], rbind)
    
    # Final results
    results <- list(best_AIC = all_models[which.min(all_models$AIC), ], # Model with best AIC
                    best_BIC = all_models[which.min(all_models$BIC), ], # Model with best BIC
                    all_models = all_models)
    return(results)
}