import io,json,unittest,urllib.error
from unittest.mock import patch
from ark_client import ArkClient,ArkError,endpoint

class TransportTests(unittest.TestCase):
 def client(self):
  c=ArkClient();c.key='test-only';c.models=['first','second'];return c
 def response(self):
  return io.BytesIO(b'data: {"choices":[{"delta":{"content":"ok"}}]}\n\ndata: [DONE]\n\n')
 def test_endpoint(self):
  self.assertEqual(endpoint('https://ark.cn-beijing.volces.com/api/v3'),'https://ark.cn-beijing.volces.com/api/v3/chat/completions')
 def test_quota_switch(self):
  c=self.client();error=urllib.error.HTTPError(c.url,429,'quota',{},io.BytesIO(b'{"error":{"code":"InsufficientQuota"}}'))
  with patch('urllib.request.urlopen',side_effect=[error,self.response()]) as call:
   self.assertEqual(c.complete([]),'ok');self.assertEqual(call.call_count,2);self.assertIn('first',c.exhausted)
 def test_auth_does_not_switch(self):
  c=self.client();error=urllib.error.HTTPError(c.url,401,'auth',{},io.BytesIO(b'{}'))
  with patch('urllib.request.urlopen',side_effect=error) as call:
   with self.assertRaises(ArkError):c.complete([])
   self.assertEqual(call.call_count,1);self.assertFalse(c.exhausted)
 def test_rate_limit_does_not_switch(self):
  c=self.client();error=urllib.error.HTTPError(c.url,429,'rate',{},io.BytesIO(b'{"error":{"code":"RateLimitExceeded"}}'))
  with patch('urllib.request.urlopen',side_effect=error) as call:
   with self.assertRaises(ArkError):c.complete([])
   self.assertEqual(call.call_count,1)
 def test_truncated_stream_rejected(self):
  with patch('urllib.request.urlopen',return_value=io.BytesIO(b'data: {"choices":[{"delta":{"content":"partial"}}]}\n\n')):
   with self.assertRaises(ArkError):self.client().complete([])
 def test_missing_key(self):
  c=self.client();c.key=''
  with self.assertRaises(ArkError):c.complete([])
 def test_route_and_stream(self):
  import app
  client=app.app.test_client()
  with patch.object(app.ark,'events',return_value=iter([{'type':'delta','text':'hello'}])):
   r=client.post('/api/ask-jj-stream',json={'question':'test'})
   self.assertIn('text/event-stream',r.content_type);self.assertIn('"type": "done"',r.text)
  self.assertEqual(client.post('/api/ask-jj-stream',json={'question':''}).status_code,400)
 def test_all_chapters(self):
  import app
  client=app.app.test_client()
  for i in range(1,10):
   r=client.get('/chapter/'+str(i));self.assertEqual(r.status_code,200);self.assertIn('vendor/three.min.js',r.text)

 def test_knowledge_universe_matches_courses(self):
  import app
  client=app.app.test_client()
  page=client.get('/stars')
  self.assertEqual(page.status_code,200)
  self.assertIn('knowledge_stars.js',page.text)
  data=client.get('/api/knowledge-universe').json
  self.assertTrue(data['success'])
  self.assertEqual(data['summary']['galaxies'],9)
  self.assertEqual(data['summary']['stars'],40)
  self.assertEqual(len(data['galaxies'][7]['stars']),8)
  self.assertEqual(data['galaxies'][7]['stars'][0]['url'],'/chapter/8#kp-1')

if __name__=='__main__':unittest.main()
