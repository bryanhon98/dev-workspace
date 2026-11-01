"""Fictional-data tests for grouping, source boundaries and artifact generation."""
import copy,json,sys,tempfile,unittest
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'scripts'))
from build_atlas import prepare,build,source_path
from java_reader import extract_statements

class AtlasTests(unittest.TestCase):
    def setUp(self):
        self.workspace=Path.cwd()/'.atlas-test-work';self.workspace.mkdir(exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=self.workspace);self.addCleanup(self.temp.cleanup)
        self.output=Path(self.temp.name)/'output'
        self.manifest=BASE/'tests/example-atlas.json'

    def test_multiline_call_and_enum_arguments_survive(self):
        data=prepare(json.loads(self.manifest.read_text()),self.manifest.parent)
        rows=data['functions'][0]['statements'];log=rows[0]
        self.assertEqual(log['line'],7);self.assertEqual(log['end_line'],8)
        self.assertIn('Json.stringify(event)',log['code']);self.assertEqual(log['kind'],'context')
        self.assertFalse(any(row['line']==8 for row in rows))
        self.assertTrue(any('execute(event, DispatchAction.CREATE_LABEL)' in row['code'] for row in rows))
        guard=next(row for row in rows if row['kind']=='decision')
        self.assertIn('event != null',guard['code']);self.assertIn('Error.INVALID_EVENT',guard['code'])
        self.assertEqual(data['functions'][0]['display_path'],'parcel-app/ShipmentRouter.java')

    def test_callback_contents_and_string_delimiters(self):
        rows=extract_statements('''template.execute(request, new Callback() {
 public void process() {
  Log.info("a;b{c}", Json.stringify(event));
  engine.execute(event, DispatchAction.CREATE_LABEL);
 }
});''',12)
        self.assertTrue(any(row['code'].startswith('Log.info') and '"a;b{c}"' in row['code'] for row in rows))
        self.assertTrue(any(row['code'].startswith('engine.execute') for row in rows))

    def test_source_traversal_and_credentials_are_rejected(self):
        root=self.manifest.parent/'fixtures/parcel-app'
        with self.assertRaises(ValueError):source_path(root,'../outside.java')
        env=root/'.env.test'
        # Rejection occurs before any content is read; a fixture need not be created.
        with self.assertRaises(ValueError):source_path(root,'.env.test')
        self.assertFalse(env.exists())

    def test_build_has_offline_viewer_and_bound_diagram_exports(self):
        report=build(self.manifest,self.output)
        self.assertEqual(report['pages'],1);self.assertFalse(report['runtime_executed'])
        text=(self.output/'index.html').read_text()
        self.assertIn('Where it comes from',text);self.assertIn('What happens next',text)
        self.assertIn('#101b2b',text);self.assertIn('DispatchAction.CREATE_LABEL',text)
        self.assertNotIn('<script src=',text);self.assertNotIn('__READER_JS__',text)
        ex=json.loads((self.output/'O1.excalidraw').read_text());elements={e['id']:e for e in ex['elements']}
        self.assertEqual(len(elements),len(ex['elements']))
        for element in elements.values():
            if element['type']=='arrow':
                self.assertIn(element['startBinding']['elementId'],elements)
                self.assertIn(element['endBinding']['elementId'],elements)
        with self.assertRaises(ValueError):build(self.manifest,self.output)

    def test_non_java_units_require_actual_source_text(self):
        root=Path(self.temp.name);(root/'example.py').write_text('def route(event):\n    return event["id"]\n')
        data=json.loads(self.manifest.read_text());data['repositories']=[{'id':'sample','root':str(root)}]
        data['functions']=[{'id':'py','repo':'sample','path':'example.py','class':'example','method':'route','line':1,'end_line':2,'signature':'def route(event):','statements':[{'line':2,'end_line':2,'code':'return event["id"]','kind':'action','meaning':'Return the event identifier.'}]}]
        data['pages'][0]['nodes']=data['pages'][0]['nodes'][:1];data['pages'][0]['nodes'][0]['function_id']='py';data['pages'][0]['edges']=[]
        self.assertEqual(prepare(data,root)['functions'][0]['statements'][0]['code'],'return event["id"]')
        bad=copy.deepcopy(data);bad['functions'][0]['statements'][0]['code']='return invented_value'
        with self.assertRaises(ValueError):prepare(bad,root)

    def test_explanations_and_relationships_are_required(self):
        data=json.loads(self.manifest.read_text());data['pages'][0]['edges'][0]['explanation']=''
        with self.assertRaises(ValueError):prepare(data,self.manifest.parent)
        data=json.loads(self.manifest.read_text());data['pages'][0]['nodes'][0]['reader']['steps']=[]
        with self.assertRaises(ValueError):prepare(data,self.manifest.parent)

if __name__=='__main__':unittest.main()
