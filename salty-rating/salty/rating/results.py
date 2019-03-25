import pandas as pd
import numpy as np


def calculate_totals(results_list):
    v_res, v_count = calculate_mean_scores([r['ratings'] for r in results_list if not r['is_judge']])
    j_res, j_count = calculate_mean_scores([r['ratings'] for r in results_list if r['is_judge']])
    results = pd.DataFrame({
        'Judges': j_res,
        'Audience': v_res,
        'Judges Cnt': j_count.fillna(0),
        'Audience Cnt': v_count.fillna(0),
    })
    results['Total'] = results[['Judges', 'Audience']].mean(axis=1, skipna=True)
    results['Count'] = results[['Judges Cnt', 'Audience Cnt']].sum(axis=1, skipna=True)
    results.sort_values('Total', ascending=False, inplace=True)
    return results


def calculate_mean_scores(ratings_list):
    df = pd.DataFrame(ratings_list)
    df = df.replace(0, np.nan)
    return df.mean(axis=0, skipna=True), df.count(axis=0)
