from backend.data_loader import get_tracking_report
r = get_tracking_report()
print('TOTALS', r['totals'])
for s in r['species']:
    print(f"{s['species']}|csv={s['csv_count']}|individuals={s['individual_count']}|points={s['point_count']}|removed={s['removed_point_count']}")
