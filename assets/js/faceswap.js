// JL Fitness — Face Fun
//
// Live-selfie-only "cutout board" photo booth. The only face this ever
// reads is a live webcam frame of the person using the page, and the only
// thing it's placed into is original artwork drawn locally in this file —
// never another photo, uploaded or otherwise. Everything runs in the
// browser; no image or video data is ever sent anywhere.

(function () {
  const root = document.getElementById('faceswap-app');
  if (!root) return;

  const CANVAS_W = 800;
  const CANVAS_H = 1000;

  /* ---- Templates -----------------------------------------------------
     Each template is drawn procedurally on an offscreen canvas, with an
     elliptical hole punched out (destination-out) where the aligned
     selfie shows through. `hole` gives the hole geometry and the target
     eye-line the live face gets aligned to. */
  const TEMPLATES = [
    {
      id: 'champion',
      name: 'Champion',
      hole: { cx: 400, cy: 300, rx: 150, ry: 190 },
      eyeLine: { y: 272, halfSpan: 75 },
      draw(ctx) {
        const g = ctx.createLinearGradient(0, 0, 0, CANVAS_H);
        g.addColorStop(0, '#1f1f1f');
        g.addColorStop(1, '#0d0d0d');
        ctx.fillStyle = g;
        ctx.fillRect(0, 0, CANVAS_W, CANVAS_H);

        // glow ring behind the hole
        ctx.save();
        ctx.beginPath();
        ctx.arc(400, 300, 230, 0, Math.PI * 2);
        const glow = ctx.createRadialGradient(400, 300, 150, 400, 300, 230);
        glow.addColorStop(0, 'rgba(200,244,0,0.22)');
        glow.addColorStop(1, 'rgba(200,244,0,0)');
        ctx.fillStyle = glow;
        ctx.fill();
        ctx.restore();

        // shoulders / torso silhouette
        ctx.fillStyle = '#1f1f1f';
        ctx.strokeStyle = '#c8f400';
        ctx.lineWidth = 6;
        ctx.beginPath();
        ctx.moveTo(180, 1000);
        ctx.quadraticCurveTo(200, 640, 340, 560);
        ctx.quadraticCurveTo(400, 520, 460, 560);
        ctx.quadraticCurveTo(600, 640, 620, 1000);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        // belt banner
        ctx.save();
        ctx.translate(400, 760);
        ctx.rotate(-0.04);
        ctx.fillStyle = '#e03030';
        ctx.fillRect(-230, -46, 460, 92);
        ctx.fillStyle = '#0d0d0d';
        ctx.font = '800 54px "Barlow Condensed", Impact, sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('CHAMPION', 0, 4);
        ctx.restore();

        // small dumbbell accents
        drawDumbbell(ctx, 120, 900, 0.9);
        drawDumbbell(ctx, 680, 900, 0.9);
      },
    },
    {
      id: 'legend',
      name: 'Gym Legend',
      hole: { cx: 400, cy: 310, rx: 155, ry: 195 },
      eyeLine: { y: 280, halfSpan: 78 },
      draw(ctx) {
        const g = ctx.createLinearGradient(0, 0, CANVAS_W, CANVAS_H);
        g.addColorStop(0, '#161616');
        g.addColorStop(1, '#0d0d0d');
        ctx.fillStyle = g;
        ctx.fillRect(0, 0, CANVAS_W, CANVAS_H);

        // weight-plate halo
        ctx.save();
        ctx.strokeStyle = '#c8f400';
        ctx.lineWidth = 22;
        ctx.beginPath();
        ctx.arc(400, 310, 235, 0, Math.PI * 2);
        ctx.stroke();
        ctx.lineWidth = 4;
        ctx.strokeStyle = '#0d0d0d';
        ctx.beginPath();
        ctx.arc(400, 310, 235, 0, Math.PI * 2);
        ctx.stroke();
        ctx.restore();

        // cape
        ctx.fillStyle = '#e03030';
        ctx.beginPath();
        ctx.moveTo(260, 560);
        ctx.quadraticCurveTo(120, 760, 160, 1000);
        ctx.lineTo(400, 900);
        ctx.lineTo(640, 1000);
        ctx.quadraticCurveTo(680, 760, 540, 560);
        ctx.closePath();
        ctx.fill();

        // torso
        ctx.fillStyle = '#1f1f1f';
        ctx.strokeStyle = '#c8f400';
        ctx.lineWidth = 6;
        ctx.beginPath();
        ctx.moveTo(230, 1000);
        ctx.quadraticCurveTo(250, 660, 360, 580);
        ctx.quadraticCurveTo(400, 550, 440, 580);
        ctx.quadraticCurveTo(550, 660, 570, 1000);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        // banner
        ctx.save();
        ctx.translate(400, 130);
        ctx.fillStyle = '#c8f400';
        ctx.fillRect(-190, -34, 380, 68);
        ctx.fillStyle = '#0d0d0d';
        ctx.font = '800 42px "Barlow Condensed", Impact, sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('LEGEND', 0, 3);
        ctx.restore();

        drawBolt(ctx, 110, 300);
        drawBolt(ctx, 690, 300);
      },
    },
    {
      id: 'strongman',
      name: 'Strongman',
      hole: { cx: 400, cy: 360, rx: 150, ry: 190 },
      eyeLine: { y: 332, halfSpan: 75 },
      draw(ctx) {
        const g = ctx.createLinearGradient(0, 0, 0, CANVAS_H);
        g.addColorStop(0, '#1f1f1f');
        g.addColorStop(1, '#0d0d0d');
        ctx.fillStyle = g;
        ctx.fillRect(0, 0, CANVAS_W, CANVAS_H);

        // striped top banner like a strongman-show tent
        ctx.save();
        for (let i = 0; i < 10; i++) {
          ctx.fillStyle = i % 2 === 0 ? '#c8f400' : '#e03030';
          ctx.beginPath();
          ctx.moveTo(i * 80, 0);
          ctx.lineTo(i * 80 + 80, 0);
          ctx.lineTo(i * 80 + 40, 70);
          ctx.closePath();
          ctx.fill();
        }
        ctx.restore();

        // barbell held overhead
        ctx.strokeStyle = '#888888';
        ctx.lineWidth = 14;
        ctx.beginPath();
        ctx.moveTo(160, 210);
        ctx.lineTo(640, 210);
        ctx.stroke();
        ctx.fillStyle = '#1f1f1f';
        ctx.strokeStyle = '#c8f400';
        ctx.lineWidth = 5;
        [150, 200, 600, 650].forEach((x, i) => {
          const r = i < 2 ? 42 : 42;
          ctx.beginPath();
          ctx.arc(x, 210, r, 0, Math.PI * 2);
          ctx.fill();
          ctx.stroke();
        });

        // arms + torso
        ctx.fillStyle = '#1f1f1f';
        ctx.strokeStyle = '#c8f400';
        ctx.lineWidth = 6;
        ctx.beginPath();
        ctx.moveTo(200, 1000);
        ctx.quadraticCurveTo(150, 760, 220, 560);
        ctx.quadraticCurveTo(260, 480, 300, 480);
        ctx.lineTo(330, 620);
        ctx.quadraticCurveTo(400, 590, 470, 620);
        ctx.lineTo(500, 480);
        ctx.quadraticCurveTo(540, 480, 580, 560);
        ctx.quadraticCurveTo(650, 760, 600, 1000);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        ctx.save();
        ctx.translate(400, 860);
        ctx.fillStyle = '#e03030';
        ctx.fillRect(-210, -40, 420, 80);
        ctx.fillStyle = '#ffffff';
        ctx.font = '800 40px "Barlow Condensed", Impact, sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('STRONGMAN', 0, 3);
        ctx.restore();
      },
    },
  ];

  function drawDumbbell(ctx, x, y, scale) {
    ctx.save();
    ctx.translate(x, y);
    ctx.scale(scale, scale);
    ctx.fillStyle = '#c8f400';
    ctx.fillRect(-40, -8, 80, 16);
    ctx.fillRect(-52, -22, 16, 44);
    ctx.fillRect(36, -22, 16, 44);
    ctx.restore();
  }

  function drawBolt(ctx, x, y) {
    ctx.save();
    ctx.translate(x, y);
    ctx.fillStyle = '#c8f400';
    ctx.beginPath();
    ctx.moveTo(10, -30);
    ctx.lineTo(-14, 6);
    ctx.lineTo(2, 6);
    ctx.lineTo(-8, 34);
    ctx.lineTo(18, -4);
    ctx.lineTo(2, -4);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  }

  function buildTemplateCanvas(tpl) {
    const c = document.createElement('canvas');
    c.width = CANVAS_W;
    c.height = CANVAS_H;
    const ctx = c.getContext('2d');
    tpl.draw(ctx);
    // punch the transparent hole the live face will show through
    ctx.save();
    ctx.globalCompositeOperation = 'destination-out';
    ctx.beginPath();
    ctx.ellipse(tpl.hole.cx, tpl.hole.cy, tpl.hole.rx, tpl.hole.ry, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
    return c;
  }

  const templateCanvases = new Map();
  TEMPLATES.forEach((t) => templateCanvases.set(t.id, buildTemplateCanvas(t)));

  /* ---- DOM ------------------------------------------------------------ */
  const els = {
    picker: root.querySelector('.template-picker'),
    stage: root.querySelector('[data-stage]'),
    video: root.querySelector('[data-video]'),
    startBtn: root.querySelector('[data-start]'),
    captureBtn: root.querySelector('[data-capture]'),
    retakeBtn: root.querySelector('[data-retake]'),
    downloadBtn: root.querySelector('[data-download]'),
    changeTplBtn: root.querySelector('[data-change-template]'),
    resultCanvas: root.querySelector('[data-result]'),
    status: root.querySelector('[data-status]'),
    countdown: root.querySelector('[data-countdown]'),
    videoWrap: root.querySelector('[data-video-wrap]'),
  };

  let selectedTemplateId = TEMPLATES[0].id;
  let stream = null;
  let faceDetector = null;
  let detectorReady = false;

  function setStatus(msg, isError) {
    if (!els.status) return;
    els.status.textContent = msg || '';
    els.status.classList.toggle('is-error', !!isError);
  }

  /* ---- Template picker -------------------------------------------------*/
  function renderPicker() {
    if (!els.picker) return;
    els.picker.innerHTML = '';
    TEMPLATES.forEach((tpl) => {
      const card = document.createElement('button');
      card.type = 'button';
      card.className = 'template-card' + (tpl.id === selectedTemplateId ? ' is-active' : '');
      card.dataset.id = tpl.id;
      const thumb = document.createElement('canvas');
      thumb.width = 160;
      thumb.height = 200;
      const tctx = thumb.getContext('2d');
      tctx.drawImage(templateCanvases.get(tpl.id), 0, 0, CANVAS_W, CANVAS_H, 0, 0, 160, 200);
      tctx.fillStyle = 'rgba(240,240,240,0.14)';
      tctx.beginPath();
      const h = tpl.hole;
      tctx.ellipse((h.cx / CANVAS_W) * 160, (h.cy / CANVAS_H) * 200, (h.rx / CANVAS_W) * 160, (h.ry / CANVAS_H) * 200, 0, 0, Math.PI * 2);
      tctx.fill();
      card.appendChild(thumb);
      const label = document.createElement('span');
      label.textContent = tpl.name;
      card.appendChild(label);
      card.addEventListener('click', () => {
        selectedTemplateId = tpl.id;
        renderPicker();
      });
      els.picker.appendChild(card);
    });
  }
  renderPicker();

  /* ---- Face detector (MediaPipe Tasks Vision, loaded lazily) ---------- */
  async function ensureDetector() {
    if (detectorReady) return faceDetector;
    setStatus('Loading face detection…');
    const { FaceDetector, FilesetResolver } = await import(
      'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14'
    );
    const files = await FilesetResolver.forVisionTasks(
      'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm'
    );
    faceDetector = await FaceDetector.createFromOptions(files, {
      baseOptions: {
        modelAssetPath:
          'https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite',
      },
      runningMode: 'IMAGE',
    });
    detectorReady = true;
    setStatus('');
    return faceDetector;
  }

  /* ---- Camera ----------------------------------------------------------*/
  async function startCamera() {
    setStatus('Requesting camera access…');
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user', width: { ideal: 1280 }, height: { ideal: 960 } },
        audio: false,
      });
    } catch (err) {
      setStatus('Camera access was denied or unavailable. Allow camera access and try again.', true);
      return;
    }
    els.video.srcObject = stream;
    await els.video.play();
    setState('camera');
    setStatus('Center your face, then hit Capture.');
    ensureDetector().catch(() => setStatus('Could not load face detection. Check your connection and retry.', true));
  }

  function stopCamera() {
    if (stream) {
      stream.getTracks().forEach((t) => t.stop());
      stream = null;
    }
  }

  /* ---- States ------------------------------------------------------------
     idle -> camera -> result */
  function setState(state) {
    root.dataset.state = state;
  }

  /* ---- Capture + compose ------------------------------------------------*/
  async function capture() {
    if (!els.video.videoWidth) {
      setStatus('Camera is still starting up — try again in a second.', true);
      return;
    }
    els.captureBtn.disabled = true;
    setStatus('Detecting your face…');

    const frameCanvas = document.createElement('canvas');
    frameCanvas.width = els.video.videoWidth;
    frameCanvas.height = els.video.videoHeight;
    frameCanvas.getContext('2d').drawImage(els.video, 0, 0);

    let detections = [];
    try {
      const detector = await ensureDetector();
      const result = detector.detect(frameCanvas);
      detections = (result && result.detections) || [];
    } catch (err) {
      setStatus('Face detection failed to load. Check your connection and try again.', true);
      els.captureBtn.disabled = false;
      return;
    }

    if (detections.length === 0) {
      setStatus('No face detected — face the camera in good lighting and try again.', true);
      els.captureBtn.disabled = false;
      return;
    }
    if (detections.length > 1) {
      setStatus('Multiple faces detected — make sure it’s just you in frame.', true);
      els.captureBtn.disabled = false;
      return;
    }

    const kp = detections[0].keypoints; // [rightEye, leftEye, nose, mouth, rightEar, leftEar] (normalized)
    if (!kp || kp.length < 2) {
      setStatus('Could not find eye landmarks — try facing the camera more directly.', true);
      els.captureBtn.disabled = false;
      return;
    }

    const fw = frameCanvas.width;
    const fh = frameCanvas.height;
    const rEye = { x: kp[0].x * fw, y: kp[0].y * fh };
    const lEye = { x: kp[1].x * fw, y: kp[1].y * fh };
    const dist = Math.hypot(lEye.x - rEye.x, lEye.y - rEye.y);

    if (dist < fw * 0.02) {
      setStatus('Face is too far / angled for a clean align — move closer and face forward.', true);
      els.captureBtn.disabled = false;
      return;
    }

    composite(frameCanvas, rEye, lEye);
    els.captureBtn.disabled = false;
    setState('result');
    setStatus('');
  }

  function composite(frameCanvas, rEye, lEye) {
    const tpl = TEMPLATES.find((t) => t.id === selectedTemplateId) || TEMPLATES[0];
    const out = els.resultCanvas;
    out.width = CANVAS_W;
    out.height = CANVAS_H;
    const ctx = out.getContext('2d');
    ctx.clearRect(0, 0, CANVAS_W, CANVAS_H);

    const targetR = { x: tpl.hole.cx - tpl.eyeLine.halfSpan, y: tpl.eyeLine.y };
    const targetL = { x: tpl.hole.cx + tpl.eyeLine.halfSpan, y: tpl.eyeLine.y };
    const targetDist = Math.hypot(targetL.x - targetR.x, targetL.y - targetR.y);
    const detectedDist = Math.hypot(lEye.x - rEye.x, lEye.y - rEye.y);
    const scale = targetDist / detectedDist;

    const detectedAngle = Math.atan2(lEye.y - rEye.y, lEye.x - rEye.x);
    const targetAngle = Math.atan2(targetL.y - targetR.y, targetL.x - targetR.x);
    const rotate = targetAngle - detectedAngle;

    const midDetected = { x: (rEye.x + lEye.x) / 2, y: (rEye.y + lEye.y) / 2 };
    const midTarget = { x: (targetR.x + targetL.x) / 2, y: (targetR.y + targetL.y) / 2 };

    ctx.save();
    ctx.translate(midTarget.x, midTarget.y);
    ctx.rotate(rotate);
    ctx.scale(scale, scale);
    ctx.translate(-midDetected.x, -midDetected.y);
    ctx.drawImage(frameCanvas, 0, 0);
    ctx.restore();

    ctx.drawImage(templateCanvases.get(tpl.id), 0, 0);
  }

  /* ---- Wiring ------------------------------------------------------------*/
  if (els.startBtn) els.startBtn.addEventListener('click', startCamera);
  if (els.captureBtn) els.captureBtn.addEventListener('click', capture);
  if (els.retakeBtn) {
    els.retakeBtn.addEventListener('click', () => {
      setState('camera');
      setStatus('Center your face, then hit Capture.');
    });
  }
  if (els.changeTplBtn) {
    els.changeTplBtn.addEventListener('click', () => {
      stopCamera();
      setState('idle');
    });
  }
  if (els.downloadBtn) {
    els.downloadBtn.addEventListener('click', () => {
      const link = document.createElement('a');
      link.download = 'jl-fitness-face-fun.png';
      link.href = els.resultCanvas.toDataURL('image/png');
      link.click();
    });
  }

  window.addEventListener('beforeunload', stopCamera);

  setState('idle');
})();
