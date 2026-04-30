import yaml
from datetime import datetime

class AuditReporter:
    @staticmethod
    def generate_report(results: list, schema_version: str = "1.0") -> str:
        if not results: return "Error: No data."
        rel = [r for r in results if r.get('status')=='success' and r.get('reliable')]
        if not rel: return yaml.dump({'status':'no_reliable_data'})
        mi_vals = [r['mi_estimate'] for r in rel]
        rep = {
            'metadata': {'timestamp': datetime.now().isoformat(), 'framework': 'PACIF v3.0', 'schema': schema_version},
            'summary': {
                'total': len(results), 'reliable': len(rel),
                'exclusion_rate': 1 - len(rel)/len(results),
                'median_mi': sorted(mi_vals)[len(mi_vals)//2],
                'mean_mi': sum(mi_vals)/len(mi_vals)
            },
            'flags': []
        }
        if rep['summary']['exclusion_rate'] > 0.4:
            rep['flags'].append('HIGH_EXCLUSION_RATE')
        return yaml.dump(rep, default_flow_style=False)
