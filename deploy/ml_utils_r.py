import pandas as pd
import re
import joblib as jb
from scipy.sparse import hstack, csr_matrix
import numpy as np
import json

mdl_rf = jb.load("random_forest_20200727.pkl.z")
title_vec_rf = jb.load("title_vectorizer_rf_20200727.pkl.z")

mdl_lgbm = jb.load("lgbm_20200727.pkl.z")
title_vec_lgbm = jb.load("title_vectorizer_lgbm_20200727.pkl.z")

def transform_all(shoes_json_data,shoes):
    
    features=dict()
           
    def tipos(feature,shoes_json_data,lista_tipos,size_prefix):
        
        for tipos in lista_tipos:
            col= feature
            
            try:
                if tipos[size_prefix:] in shoes_json_data[col]:
                    features[tipos]=1
                else:
                    features[tipos]=0
            except:
                features[tipos]=0
        
        return features
    
    
    try:
        features['shoes_name']=shoes['name']
    except:
        features['shoes_name']='sem nome?'
        
    try:
        features['link']=shoes['link']
    except:
        features['link']='erro link'
    
    try:
        features['image']=shoes_json_data['image']
    except:
        features['image']='erro link imagem' 
        
    try:
        features['reasons_not_to_buy']=int(shoes_json_data['reasons_not_to_buy'])
    except:
        features['reasons_not_to_buy']=0 
    
    try:
        features['reasons_to_buy']=int(shoes_json_data['reasons_to_buy'])
    except:
        features['reasons_to_buy']=0
    
    try:
        features['bad_reasons_to_buy']=shoes_json_data['bad_reasons_to_buy']
    except:
        features['bad_reasons_to_buy']=''
        
    try:
        features['good_reasons_to_buy']=shoes_json_data['good_reasons_to_buy']
    except:
        features['good_reasons_to_buy']=''
        
          
    tiposs=['terrain_Road', 'terrain_Trail', 'terrain_Treadmill', 'terrain_Mud','terrain_Snow']     
    features=tipos('terrain-value',shoes_json_data,tiposs,8)   
        
    tiposs=['arch_Neutral', 'arch_Stability', 'arch_Motion control']       
    features=tipos('arch-support-value',shoes_json_data,tiposs,5)
    
    tiposs=['Neutral Pronation', 'Overpronation', 'Severe overpronation']
    features=tipos('pronation-value',shoes_json_data,tiposs,0)   
    
    tiposs=['archtype_High arch', 'archtype_Medium arch', 'archtype_Low arch']
    features=tipos('arch-type-value',shoes_json_data,tiposs,9)
    
    tiposs=['use_Jogging', 'use_All-day wear', 'use_Fell running', 'use_Walking','use_Triathlon', 'use_Obstacle course racing']
    features=tipos('use-value',shoes_json_data,tiposs,4)
    
    tiposs=[
        'brand_Asics','brand_Nike', 'brand_Adidas', 'brand_New Balance', 'brand_Saucony',
        'brand_Reebok', 'brand_Brooks', 'brand_Salomon', 'brand_Under Armour',
        'brand_Mizuno', 'brand_Puma', 'brand_Hoka One One', 'brand_Merrell',
        'brand_Altra', 'brand_Inov-8', 'brand_Skechers', 'brand_Newton',
        'brand_On', 'brand_The North Face', 'brand_La Sportiva',
        'brand_Topo Athletic', 'brand_361 Degrees', 'brand_Zoot',
        'brand_Vibram FiveFingers', 'brand_Scott', 'brand_Dynafit',
        'brand_Vivobarefoot', 'brand_Jordan', 'brand_Salming',
        "brand_Arc'teryx", 'brand_Xero Shoes', 'brand_Icebug', 'brand_Columbia',
           ]
    features=tipos('brand-value',shoes_json_data,tiposs,6)
    
    tiposs=[
         'type_Heavy', 'type_Big guy', 'type_Low drop', 'type_Zero drop',
         'type_Maximalist', 'type_Barefoot', 'type_Minimalist'
           ] 
    features=tipos('type-value',shoes_json_data,tiposs,5)
    
    tiposs=['width_Normal','width_Wide', 'width_X-Wide', 'width_Narrow']
    features=tipos('width-value',shoes_json_data,tiposs,6)
    
    tiposs=['strike_Midfoot strike','strike_Heel strike', 'strike_Forefoot strike']
    features=tipos('strike-pattern-value',shoes_json_data,tiposs,7)
    
    tiposs=['dist_Daily running','dist_Long distance', 'dist_Marathon', 'dist_Competition','dist_Ultra running']
    features=tipos('distance-value',shoes_json_data,tiposs,7)
    
    
    def men_women(feature,shoes_json_data,medida):  
        try:
            row= shoes_json_data[feature]
            if re.findall('Men: (\d+)'+medida,row)!=[]:
                features[feature+'_men']= int(re.findall('Men: (\d+)'+medida,row)[0])
            else:
                features[feature+'_men']=-1
        except:
            
            features[feature+'_men']=-1
            
        try:
            if re.findall('Women: (\d+)'+medida,row)!=[]:
                features[feature+'_women']= int(re.findall('Women: (\d+)'+medida,row)[0])
            else:
                features[feature+'_women']=-1
        except:
            
            features[feature+'_women']=-1
        
        return features
    
    features=men_women('forefoot-height-value',shoes_json_data,'mm')
    features=men_women('heel-height-value',shoes_json_data,'mm')
    features=men_women('heel-to-toe-drop-value',shoes_json_data,'mm')
    features=men_women('weight-value',shoes_json_data,'mm')
    
    
    try:
        row=shoes_json_data['price-value']
        if re.findall('(\d+)',row)!=[]:
            features['price']= int(re.findall('(\d+)',row)[0])
        else:
            features['price']=-1
    except:
        features['price']=-1
            
    try:
        row=shoes_json_data['rr-reviews-score-average']
        if re.findall('(\d+)',row)!=[]:
            features['expert_score']= int(re.findall('(\d+)',row)[0])
            features['n_expert_reviews']= int(re.findall('(\d+)',row)[2])          
        else:
            features['expert_score']= -1
            features['n_expert_reviews']= -1
    except:
        features['expert_score']= -1
        features['n_expert_reviews']= -1
        
    
    try:
        row=shoes_json_data['release-date-value']
        if re.findall('(\d+)',row)!=[]:
            features['release_year']= int(re.findall('(\d+)',row)[0])          
        else:
            features['release_year']= -1
    except:
        features['release_year']= -1
        
    
    try:
        row=shoes_json_data['update-value']
        if row != None:
            features['older_version']= 1         
        else:
            features['older_version']= 0
    except:
        features['older_version']= -1
        
    try:
        row=shoes_json_data['update-value']
        if row != None:
            features['older_version']= 1         
        else:
            features['older_version']= 0
    except:
        features['older_version']= -1
        
        
    try:
        if [value for key, value in shoes_json_data.items() if 'better rated than the previous version' in key.lower()] != []:
            features['is_a_better_upgraded_version']=1
        else:
            features['is_a_better_upgraded_version']=0
    except:
        features['is_a_better_upgraded_version']=0
        
    try:
        if [value for key, value in shoes_json_data.items() if r"a top (\d+)%" in key.lower()] != []:
            features['is_a_top_percent']=1
        else:
            features['is_a_top_percent']=0
    except:
        features['is_a_top_percent']=0
        
    try:
        if [value for key, value in shoes_json_data.items() if r"a top rated" in key.lower()] != []:
            features['is_a_top_rated']=1
        else:
            features['is_a_top_rated']=0
    except:
        features['is_a_top_rated']=0
    
    return features

def compute_features(array):

    index=[
         'reasons_not_to_buy','reasons_to_buy','terrain_Road','terrain_Trail','terrain_Treadmill','terrain_Mud','terrain_Snow',
         'arch_Neutral','arch_Stability','arch_Motion control','Neutral Pronation','Overpronation','Severe overpronation',
         'archtype_High arch','archtype_Medium arch','archtype_Low arch','use_Jogging','use_All-day wear','use_Fell running',
         'use_Walking','use_Triathlon','use_Obstacle course racing','brand_Asics','brand_Nike','brand_Adidas','brand_New Balance',
         'brand_Saucony','brand_Reebok','brand_Brooks','brand_Salomon','brand_Under Armour','brand_Mizuno','brand_Puma','brand_Hoka One One',
         'brand_Merrell','brand_Altra','brand_Inov-8','brand_Skechers','brand_Newton','brand_On','brand_The North Face','brand_La Sportiva',
         'brand_Topo Athletic','brand_361 Degrees','brand_Zoot','brand_Vibram FiveFingers','brand_Scott','brand_Dynafit','brand_Vivobarefoot',
         'brand_Jordan','brand_Salming',"brand_Arc'teryx",'brand_Xero Shoes','brand_Icebug','brand_Columbia','type_Heavy','type_Big guy',
         'type_Low drop','type_Zero drop','type_Maximalist','type_Barefoot','type_Minimalist','width_Normal','width_Wide','width_X-Wide',
         'width_Narrow','strike_Midfoot strike','strike_Heel strike','strike_Forefoot strike','dist_Daily running','dist_Long distance',
         'dist_Marathon','dist_Competition','dist_Ultra running','forefoot-height-value_men','forefoot-height-value_women','heel-height-value_men',
         'heel-height-value_women','heel-to-toe-drop-value_men','heel-to-toe-drop-value_women','weight-value_men','weight-value_women','price',
         'expert_score','n_expert_reviews','release_year','older_version','is_a_better_upgraded_version','is_a_top_percent','is_a_top_rated'
          ]

    reordered_array = {k: array[k] for k in index}

    title=array['good_reasons_to_buy']

    vectorized_title_rf = title_vec_rf.transform([title])
    vectorized_title_lgbm = title_vec_lgbm.transform([title])

    num_features = csr_matrix(np.array([k for k in reordered_array.values()]))

    feature_array_rf   = hstack([num_features, vectorized_title_rf])
    feature_array_lgbm = hstack([num_features, vectorized_title_lgbm])

    return feature_array_rf, feature_array_lgbm


def compute_prediction(data):
    feature_array_rf, feature_array_lgbm = compute_features(data)

    p_rf = mdl_rf.predict_proba(feature_array_rf)[0][1]
    p_lgbm = mdl_lgbm.predict_proba(feature_array_lgbm)[0][1]
    
    p = 0.5*p_rf + 0.5*p_lgbm

    return p_rf