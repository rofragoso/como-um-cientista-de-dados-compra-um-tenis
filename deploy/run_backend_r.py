from get_data_r import *
from ml_utils_r import *
import time

def update_db():
    with open("novos_tenis.json", 'w+') as output:
        
        for page in range(1,10):

            search_page = download_search_page(page)
            shoes_list=parse_search_page(search_page)

            for shoes in shoes_list:
                shoes_page=download_shoes_page(shoes['link'])
                shoes_json_data = parse_shoes_page(shoes_page)

                pre_feature_array=transform_all(shoes_json_data,shoes)
                
                p=compute_prediction(pre_feature_array)
                
                shoes_name= pre_feature_array['shoes_name']
                link= 'https://runrepeat.com'+pre_feature_array['link']
                link_image= pre_feature_array['image']
                score=p

                data_front = {"shoes": shoes_name, "score": float(p), "link": link, "image": link_image}
                data_front['update_time'] = time.time_ns()

                print(data_front)

                output.write("{}\n".format(json.dumps(data_front)))

    return True