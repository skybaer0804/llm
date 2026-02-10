## Ollama 멀티모달 이미지 입력

### 비전 모델 설치

```bash
# Scout 비전 버전 (멀티모달)
ollama pull llama4:scout-vision-q4_K_M

# 또는 Gemma3 (이미지+텍스트)
ollama pull gemma3:27b
```

### 이미지 입력 방법 1: cURL

```bash
# 로컬 파일 경로
curl http://localhost:11434/api/generate -d '{
  "model": "llama4:scout-vision",
  "prompt": "이 사진에 뭐가 찍혀있어? 누구야?",
  "images": ["photo.jpg"]
}'
```

### 이미지 입력 방법 2: Base64 (웹앱용)

```bash
IMAGE_BASE64=$(base64 -i photo.jpg)
curl http://localhost:11434/api/generate -d "{
  \"model\": \"llama4:scout-vision\",
  \"prompt\": \"이 사진 분석해줘\",
  \"images\": [\"$IMAGE_BASE64\"]
}"
```

### 웹앱 Socket.IO 연동 (Express.js)

```javascript
app.post('/api/vision', upload.single('image'), async (req, res) => {
  const imageBuffer = req.file.buffer;
  const imageBase64 = imageBuffer.toString('base64');
  
  const response = await fetch('http://localhost:11434/api/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: 'llama4:scout-vision',
      prompt: req.body.prompt || '이 사진 분석해줘',
      images: [imageBase64]
    })
  });
  
  const data = await response.json();
  io.emit('vision_reply', data.response);
  res.json(data);
});
```

**HTML 업로드:**
```html
<input type="file" id="imageUpload" accept="image/*">
<script>
document.getElementById('imageUpload').addEventListener('change', async (e) => {
  const formData = new FormData();
  formData.append('image', e.target.files[0]);
  formData.append('prompt', '가족 사진 누구야?');
  
  const res = await fetch('/api/vision', {
    method: 'POST',
    body: formData
  });
  const data = await res.json();
  console.log('AI 분석:', data.response);
});
</script>
```

### 성능 (M4 Pro 64GB)
```
이미지 1장 분석: 3~5초 (30~40 tok/s)
동시 3장: 8초
RAM 추가 사용: +2GB
```