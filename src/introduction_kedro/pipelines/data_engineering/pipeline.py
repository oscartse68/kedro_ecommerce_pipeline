from kedro.pipeline import Pipeline, node

from .nodes import hktvmall_conn_node, \
    request_hktvmall_catagory_code, gen_hktvmall_product_by_method_and_cat_links, \
    promotion_difference_raw_to_kedro_csvdataset, hot_pick_order_raw_to_kedro_csvdataset, \
    categories_df_etl, categories_df_etl_to_kedro_csvdataset, multi_threading_req


def create_pipeline(**kwargs):
    pipe = []
    # conn start
    pipe.append(
        node(
            hktvmall_conn_node,
            inputs="params:hktvmall_home_url",
            outputs="HktvmallHeader",
        )
    )
    # categories
    pipe.append(
        node(
            request_hktvmall_catagory_code,
            inputs=["HktvmallHeader", "params:hktvmall_category_diction_url"],
            outputs="Categories_raw",
        )
    )
    # categories Extract
    pipe.append(
        node(
            categories_df_etl,
            inputs="Categories_raw",
            outputs="CategoriesExtracted_df",
        )
    )
    # generate links
    pipe.append(
        node(
            gen_hktvmall_product_by_method_and_cat_links,
            inputs=['params:hktvmall_catagory_code', 'params:hktvmall_browse_method', "params:product_by_method_catcode_url"],
            outputs=dict(method1="PromotionDifferenceURL_list", method2="HotPickOrderURL_list")
        )
    )
    # get PromotionDifference_raw_df
    pipe.append(
        node(
            multi_threading_req,
            inputs=["HktvmallHeader", "PromotionDifferenceURL_list"],
            outputs="PromotionDifference_raw_df"
        )
    )
    # get HotPickOrder_raw_df
    pipe.append(
        node(
            multi_threading_req,
            inputs=["HktvmallHeader", "HotPickOrderURL_list"],
            outputs="HotPickOrder_raw_df"
        )
    )
    # turn PromotionDifference_raw_df to PromotionDifference_raw
    pipe.append(
        node(
            promotion_difference_raw_to_kedro_csvdataset,
            inputs="PromotionDifference_raw_df",
            outputs="PromotionDifference_raw"
        )
    )
    # turn HotPickOrder_raw_df to HotPickOrder_raw
    pipe.append(
        node(
            hot_pick_order_raw_to_kedro_csvdataset,
            inputs="HotPickOrder_raw_df",
            outputs="HotPickOrder_raw"
        )
    )
    # turn hktv_mall_category_extracted to HotPickOrder_raw
    pipe.append(
        node(
            categories_df_etl_to_kedro_csvdataset,
            inputs="CategoriesExtracted_df",
            outputs="CategoriesExtracted"
        )
    )

    return Pipeline(pipe)
