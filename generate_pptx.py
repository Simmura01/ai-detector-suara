import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_guardivoice_presentation(output_path):
    prs = Presentation()
    # 16:9 Widescreen
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Palet Warna Elegan & Modern
    DARK_BG = RGBColor(15, 23, 42)       # Slate 900
    DARK_CARD = RGBColor(30, 41, 59)     # Slate 800
    LIGHT_BG = RGBColor(248, 250, 252)   # Slate 50
    CARD_BG = RGBColor(255, 255, 255)    # White
    CARD_BORDER = RGBColor(226, 232, 240)# Slate 200
    PRIMARY_BLUE = RGBColor(37, 99, 235) # Blue 600
    ACCENT_SKY = RGBColor(2, 132, 199)   # Sky 600
    TEXT_DARK = RGBColor(15, 23, 42)     # Slate 900
    TEXT_MUTED = RGBColor(100, 116, 139) # Slate 500
    TEXT_LIGHT = RGBColor(241, 245, 249) # Slate 100
    EMERALD = RGBColor(5, 150, 105)      # Emerald 600
    RED_ACCENT = RGBColor(220, 38, 38)   # Red 600
    PURPLE_ACCENT = RGBColor(147, 51, 234)# Purple 600

    def add_bg(slide, color):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_header(slide, badge_text, title_text, category_text="GuardiVoice | AI Voice Detection"):
        # Top banner line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.4), Inches(11.733), Inches(0.04))
        line.fill.solid()
        line.fill.fore_color.rgb = PRIMARY_BLUE
        line.line.fill.background()

        # Category and Badge
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.55), Inches(11.733), Inches(0.9))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p = tf.paragraphs[0]
        p.text = f"{badge_text.upper()}  •  {category_text}"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_BLUE

        p2 = tf.add_paragraph()
        p2.text = title_text
        p2.font.size = Pt(22)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_DARK
        p2.space_before = Pt(4)

    def add_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        if border_color:
            card.line.color.rgb = border_color
            card.line.width = Pt(1)
        else:
            card.line.fill.background()
        return card

    # =========================================================================
    # SLIDE 1: COVER SLIDE (Dark Premium)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    add_bg(s1, DARK_BG)

    # Accent decorative box
    dec = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(1.5), Inches(0.1), Inches(4.5))
    dec.fill.solid()
    dec.fill.fore_color.rgb = PRIMARY_BLUE
    dec.line.fill.background()

    # Title box
    tb1 = s1.shapes.add_textbox(Inches(1.4), Inches(1.5), Inches(10.5), Inches(4.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "PROYEK INOVASI TEKNOLOGI BIO-AKUSTIK (IYSA / BKI 2025)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE
    p.space_after = Pt(14)

    p2 = tf1.add_paragraph()
    p2.text = "GuardiVoice"
    p2.font.size = Pt(46)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_LIGHT

    p3 = tf1.add_paragraph()
    p3.text = "Detektor Keaslian Suara AI Berbasis Algoritma BAMBS"
    p3.font.size = Pt(24)
    p3.font.bold = True
    p3.font.color.rgb = RGBColor(147, 197, 253) # Sky 300
    p3.space_before = Pt(6)
    p3.space_after = Pt(16)

    p4 = tf1.add_paragraph()
    p4.text = "Bio-Acoustic Multi-Boundary Scoring: Validasi Keaslian Suara Manusia vs Kloning AI Melalui 4 Batasan Fisik Vokal yang Transparan (Explainable AI)."
    p4.font.size = Pt(14)
    p4.font.color.rgb = RGBColor(203, 213, 225) # Slate 300
    p4.space_after = Pt(28)

    p5 = tf1.add_paragraph()
    p5.text = "Disusun oleh: Jasim & Tim Peneliti GuardiVoice  |  Teknologi: Python, FastAPI, DSP, BAMBS Engine"
    p5.font.size = Pt(11)
    p5.font.color.rgb = RGBColor(148, 163, 184) # Slate 400

    # =========================================================================
    # SLIDE 2: BAB 1 — LATAR BELAKANG & MASALAH
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_bg(s2, LIGHT_BG)
    add_header(s2, "BAB 1: Latar Belakang", "Urgensi Masalah: Ledakan Ancaman AI Voice Cloning")

    # 3 Cards Problem
    problems = [
        ("01 / ANCAMAN KLONING", "Sintesis Suara Sangat Realistis", 
         "Teknologi Neural Vocoder modern (HiFi-GAN, VITS, ElevenLabs) kini hanya membutuhkan sampel suara target berdurasi 3 detik untuk meniru timbre dan karakter vokal seseorang secara meyakinkan.",
         RED_ACCENT),
        ("02 / KERUGIAN NYATA", "Modus Vishing & Pemerasan", 
         "Marak terjadi penipuan suara darurat (voice phishing/vishing), rekayasa penculikan palsu anggota keluarga, hingga manipulasi instruksi transfer perbankan yang menyebabkan kerugian finansial masif.",
         RGBColor(217, 119, 6)),
        ("03 / DETEKTOR LEMAH", "Kelemahan Model Black-Box", 
         "Detektor deep learning konvensional bertindak sebagai kotak hitam: rentan salah prediksi jika ada noise latar, tidak dapat dijelaskan bukti forensiknya ke juri, serta membutuhkan komputasi GPU berat.",
         PRIMARY_BLUE)
    ]

    card_w = Inches(3.64)
    gap = Inches(0.4)
    left_start = Inches(0.8)
    top_pos = Inches(1.8)
    card_h = Inches(4.8)

    for i, (badge, title, desc, color) in enumerate(problems):
        c_left = left_start + i * (card_w + gap)
        add_card(s2, c_left, top_pos, card_w, card_h)
        
        # Pill top
        pill = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, c_left, top_pos, card_w, Inches(0.08))
        pill.fill.solid()
        pill.fill.fore_color.rgb = color
        pill.line.fill.background()

        tb = s2.shapes.add_textbox(c_left + Inches(0.3), top_pos + Inches(0.35), card_w - Inches(0.6), card_h - Inches(0.7))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = badge
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = color
        p.space_after = Pt(12)

        p2 = tf.add_paragraph()
        p2.text = title
        p2.font.size = Pt(16)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_DARK
        p2.space_after = Pt(14)

        p3 = tf.add_paragraph()
        p3.text = desc
        p3.font.size = Pt(12.5)
        p3.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 3: BAB 1 — SOLUSI INOVATIF: ALGORITMA BAMBS
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_bg(s3, LIGHT_BG)
    add_header(s3, "BAB 1: Solusi Sistem", "Solusi Inovatif: Algoritma BAMBS (Bio-Acoustic Multi-Boundary Scoring)")

    solutions = [
        ("PILAR 1: BIO-ACOUSTIC", "Uji Batasan Fisik Biologis", 
         "Alih-alih menebak probabilitas secara buta, BAMBS menguji apakah suara memenuhi batasan hukum mekanika laring, getaran pita suara, dan suplai respirasi biologis manusia yang gagal ditiru vocoder.",
         PRIMARY_BLUE),
        ("PILAR 2: EXPLAINABLE AI", "100% Transparan & Akuntabel", 
         "Memberikan diagnosa kuantitatif yang jelas: menyajikan nilai eksak parameter berbanding ambang batas terkalibrasi, menjadi alat bukti forensik ilmiah yang tak terbantahkan bagi juri.",
         EMERALD),
        ("PILAR 3: ULTRA-LIGHTWEIGHT", "Cepat & Mandiri Tanpa GPU", 
         "Dijalankan murni dengan komputasi Digital Signal Processing (DSP) dan aturan multi-boundary deterministik. Sangat ringan, hemat daya, serta siap dideploy di server web maupun aplikasi smartphone.",
         PURPLE_ACCENT)
    ]

    for i, (badge, title, desc, color) in enumerate(solutions):
        c_left = left_start + i * (card_w + gap)
        add_card(s3, c_left, top_pos, card_w, card_h)
        
        pill = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, c_left, top_pos, card_w, Inches(0.08))
        pill.fill.solid()
        pill.fill.fore_color.rgb = color
        pill.line.fill.background()

        tb = s3.shapes.add_textbox(c_left + Inches(0.3), top_pos + Inches(0.35), card_w - Inches(0.6), card_h - Inches(0.7))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = badge
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = color
        p.space_after = Pt(12)

        p2 = tf.add_paragraph()
        p2.text = title
        p2.font.size = Pt(16)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_DARK
        p2.space_after = Pt(14)

        p3 = tf.add_paragraph()
        p3.text = desc
        p3.font.size = Pt(12.5)
        p3.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 4: BAB 2 — 4 BATASAN AKUSTIK KUNCI (BAMBS PARAMETERS)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_bg(s4, LIGHT_BG)
    add_header(s4, "BAB 2: Arsitektur Algoritma", "Diagnosa 4 Batasan Fisik Akustik Kunci")

    # 4 Cards Grid (2x2)
    b_data = [
        ("BATASAN 01 • DINAMIKA NADA", "Pitch Range (Rentang Nada F0)", 
         "Ambang Alami: ≥ 132.56 Hz  |  Bobot: 18.9%", 
         "Mengukur fleksibilitas otot krikotiroid laring manusia. Suara AI/TTS cenderung datar dan memiliki rentang intonasi yang terbatas/monoton.",
         PRIMARY_BLUE),
        ("BATASAN 02 • PERTURBASI AMPLITUDO", "Shimmer (Fluktuasi Mikro)", 
         "Ambang Alami: ≤ 0.1163  |  Bobot: 21.7%", 
         "Mengukur konsistensi amplitudo antar-siklus vokal. Neural vocoder AI meninggalkan artifak lonjakan mikroskopis yang menghasilkan shimmer tinggi tak wajar.",
         RGBColor(217, 119, 6)),
        ("BATASAN 03 • RESPIRASI PARU", "Harmonic-to-Noise Ratio (HNR)", 
         "Ambang Alami: ≥ 2.1655 dB  |  Bobot: 20.1%", 
         "Mengukur rasio energi harmonik murni berbanding desis udara. AI tidak memiliki paru-paru biologis sehingga spektrumnya terkontaminasi distorsi kuantisasi.",
         EMERALD),
        ("BATASAN 04 • RESONANSI SALURAN VOKAL", "Dispersi Formant (MFCC-7 Std)", 
         "Ambang Alami: ≤ 14.484  |  Bobot: 39.3% (KUNCI UTAMA)", 
         "Memodelkan resonansi akustik rongga faring dan mulut (~2.5-3.5 kHz). Vocoder sintetis gagal mereplikasi transfer fungsi saluran vokal secara konsisten.",
         PURPLE_ACCENT)
    ]

    gw = Inches(5.65)
    gh = Inches(2.25)
    g_x = [Inches(0.8), Inches(6.88)]
    g_y = [Inches(1.8), Inches(4.35)]

    for idx, (badge, title, th, desc, col) in enumerate(b_data):
        col_idx = idx % 2
        row_idx = idx // 2
        bx = g_x[col_idx]
        by = g_y[row_idx]
        
        add_card(s4, bx, by, gw, gh)
        
        # Indicator bar on left
        bar = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, bx, by, Inches(0.1), gh)
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tb = s4.shapes.add_textbox(bx + Inches(0.25), by + Inches(0.2), gw - Inches(0.45), gh - Inches(0.35))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = badge
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = col

        p2 = tf.add_paragraph()
        p2.text = title
        p2.font.size = Pt(14)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_DARK
        p2.space_before = Pt(2)

        p3 = tf.add_paragraph()
        p3.text = th
        p3.font.size = Pt(11)
        p3.font.bold = True
        p3.font.color.rgb = PRIMARY_BLUE
        p3.space_before = Pt(2)
        p3.space_after = Pt(4)

        p4 = tf.add_paragraph()
        p4.text = desc
        p4.font.size = Pt(10.5)
        p4.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 5: VALIDASI EKSPERIMEN & VISUALISASI MODEL
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_bg(s5, LIGHT_BG)
    add_header(s5, "BAB 2: Bukti Ilmiah", "Hasil Kalibrasi Dataset & Validasi Akurasi 100%")

    # Left Column: Metrics summary card
    add_card(s5, Inches(0.8), Inches(1.8), Inches(4.5), Inches(4.8))
    tb_m = s5.shapes.add_textbox(Inches(1.1), Inches(2.1), Inches(3.9), Inches(4.2))
    tf_m = tb_m.text_frame
    tf_m.word_wrap = True

    p = tf_m.paragraphs[0]
    p.text = "RINGKASAN METRIK EVALUASI"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE
    p.space_after = Pt(14)

    metrics = [
        ("Akurasi Model", "100.0%", "Cross-Validation Terkalibrasi"),
        ("Nilai ROC-AUC", "1.000", "Separasi Kelas Sempurna"),
        ("Ukuran Dataset", "42 Sampel", "21 Suara Manusia & 21 Suara AI"),
        ("Parameter Kunci", "MFCC-7 Std", "Sensitivitas Tertinggi (39.3%)"),
        ("Latensi Ekstraksi", "< 0.4 Detik", "Komputasi CPU Cepat")
    ]

    for label, val, sub in metrics:
        p1 = tf_m.add_paragraph()
        p1.text = f"{label}: {val}"
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = TEXT_DARK
        p1.space_before = Pt(6)

        p2 = tf_m.add_paragraph()
        p2.text = sub
        p2.font.size = Pt(10)
        p2.font.color.rgb = TEXT_MUTED

    # Right Column: Insert plots if available
    img_models_path = r"C:\Jasim\BKI\ai detection\ai-detector-suara\models"
    cf_img = os.path.join(img_models_path, "confusion_matrix.png")
    bv_img = os.path.join(img_models_path, "boundaries_visualization.png")

    if os.path.exists(cf_img):
        add_card(s5, Inches(5.6), Inches(1.8), Inches(6.933), Inches(4.8))
        # Add confusion matrix and boundary visualization
        try:
            s5.shapes.add_picture(cf_img, Inches(5.8), Inches(2.0), width=Inches(3.2))
        except Exception as e:
            pass
        if os.path.exists(bv_img):
            try:
                s5.shapes.add_picture(bv_img, Inches(9.1), Inches(2.0), width=Inches(3.2))
            except Exception as e:
                pass

        # Caption text
        tb_c = s5.shapes.add_textbox(Inches(5.8), Inches(5.6), Inches(6.5), Inches(0.8))
        tf_c = tb_c.text_frame
        tf_c.word_wrap = True
        p = tf_c.paragraphs[0]
        p.text = "Grafik Kiri: Matriks Konfusi (Confusion Matrix) membuktikan 0 False Positive.\nGrafik Kanan: Visualisasi Distribusi 4 Ambang Batas BAMBS (Human vs AI)."
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 6: BAB 3 — MEKANISME KERJA & BENTUK DATA (4 TAHAPAN)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_bg(s6, LIGHT_BG)
    add_header(s6, "BAB 3: Mekanisme Sistem", "Alur Pengolahan Data: Dari Sinyal Audio ke Vonis Final")

    stages = [
        ("TAHAP 01", "Akuisisi & Normalisasi", 
         "Audio PCM (Mic/WAV) disampling ulang ke mono 22.050 Hz dan dinormalisasi amplitudonya ke rentang [-1.0, 1.0].",
         "Format Data:\nArray 1D float32 [N_samples]"),
        ("TAHAP 02", "Transformasi DSP", 
         "Transformasi Fourier (STFT) membedah sinyal domain waktu menjadi matriks spektrogram frekuensi & harmonik.",
         "Format Data:\nMatriks STFT (1025 x T frames)"),
        ("TAHAP 03", "Ekstraksi 4 Batasan", 
         "Algoritma menghitung kontur F0 (Pitch), fluktuasi amplitudo (Shimmer), rasio HNR, dan koefisien MFCC-7.",
         "Format Data:\nVektor: [F0, Shim, HNR, MFCC7]"),
        ("TAHAP 04", "Vonis BAMBS & Skor", 
         "Setiap batasan dievaluasi terhadap ambang batas terkalibrasi dan diagregasi menjadi keyakinan probabilistik.",
         "Format Data:\nVerdict + Confidence Score (%)")
    ]

    sw = Inches(2.72)
    sgap = Inches(0.28)
    s_top = Inches(1.8)
    s_h = Inches(4.8)

    for i, (tag, title, desc, data_fmt) in enumerate(stages):
        sx = Inches(0.8) + i * (sw + sgap)
        add_card(s6, sx, s_top, sw, s_h)

        # Header tag
        tag_box = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, sx, s_top, sw, Inches(0.5))
        tag_box.fill.solid()
        tag_box.fill.fore_color.rgb = PRIMARY_BLUE
        tag_box.line.fill.background()

        tb_tag = s6.shapes.add_textbox(sx, s_top + Inches(0.1), sw, Inches(0.3))
        p = tb_tag.text_frame.paragraphs[0]
        p.text = tag
        p.alignment = PP_ALIGN.CENTER
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_LIGHT

        # Body
        tb_body = s6.shapes.add_textbox(sx + Inches(0.2), s_top + Inches(0.65), sw - Inches(0.4), s_h - Inches(0.8))
        tf = tb_body.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = TEXT_DARK
        p1.space_after = Pt(10)

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(11)
        p2.font.color.rgb = TEXT_MUTED
        p2.space_after = Pt(16)

        # Inner Data Box
        p3 = tf.add_paragraph()
        p3.text = data_fmt
        p3.font.size = Pt(9.5)
        p3.font.bold = True
        p3.font.color.rgb = PRIMARY_BLUE

    # =========================================================================
    # SLIDE 7: BAB 4 — BEDAH ANTARMUKA APLIKASI GUARDIVOICE
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_bg(s7, LIGHT_BG)
    add_header(s7, "BAB 4: Antarmuka Aplikasi", "Bedah Tampilan Web App GuardiVoice (Minimalis & Siap Lomba)")

    # 4 UI Sections Explained
    ui_blocks = [
        ("01 / INPUT KONTROL AUDIO", "Upload Berkas & Rekam Mikrofon Live",
         "Menyediakan dua metode masukan audio: upload file rekaman (.wav, .mp3) atau rekam suara langsung via mikrofon browser. Dilengkapi visualisasi waveform real-time."),
        ("02 / SIMPLIFIKASI VONIS", "Hasil Cepat & Skor Keyakinan Model",
         "Dirancang khusus sesuai standar penilaian lomba: langsung menampilkan status jelas 'Suara Manusia Asli' vs 'Suara Sintetis AI' dengan persentase keyakinan tanpa membingungkan juri."),
        ("03 / ANALISIS MENDALAM", "Kartu Diagnosa 4 Batasan (Collapsible)",
         "Bukti forensik teknis dapat dibuka secara opsional untuk dewan juri ahli: memperlihatkan nilai Pitch, Shimmer, HNR, dan MFCC-7 berbanding ambang batas biologis manusia."),
        ("04 / ARSITEKTUR HYBRID", "Auto-Detect Local & Cloud Server",
         "Frontend cerdas mendeteksi otomatis lingkungan eksekusi: beralih mulus antara backend lokal (localhost:8000) dan production cloud hosting tanpa perlu ganti kode.")
    ]

    card_h_ui = Inches(2.25)
    for idx, (badge, title, desc) in enumerate(ui_blocks):
        c_col = idx % 2
        c_row = idx // 2
        bx = g_x[c_col]
        by = g_y[c_row]
        
        add_card(s7, bx, by, gw, card_h_ui)

        tb = s7.shapes.add_textbox(bx + Inches(0.3), by + Inches(0.2), gw - Inches(0.6), card_h_ui - Inches(0.35))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = badge
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_BLUE

        p2 = tf.add_paragraph()
        p2.text = title
        p2.font.size = Pt(14)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_DARK
        p2.space_before = Pt(3)
        p2.space_after = Pt(6)

        p3 = tf.add_paragraph()
        p3.text = desc
        p3.font.size = Pt(11)
        p3.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 8: KESIMPULAN & NILAI JUAL UNTUK LOMBA (Closing)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_bg(s8, DARK_BG)

    tb8 = s8.shapes.add_textbox(Inches(1.0), Inches(0.9), Inches(11.333), Inches(5.8))
    tf8 = tb8.text_frame
    tf8.word_wrap = True

    p = tf8.paragraphs[0]
    p.text = "KESIMPULAN & NILAI STRATEGIS PROYEK"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE
    p.space_after = Pt(8)

    p2 = tf8.add_paragraph()
    p2.text = "Mengapa GuardiVoice Unggul untuk Kompetisi IYSA & BKI?"
    p2.font.size = Pt(26)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_LIGHT
    p2.space_after = Pt(20)

    points = [
        ("Kebaruan Ilmiah (Novelty)", "Tidak bergantung pada library black-box. Mengembangkan algoritma sendiri berbasis hukum fisika akustik organ vokal biologis."),
        ("Transparansi Forensik (Explainable AI)", "Menyediakan bukti terukur per parameter; memenuhi standar audit penegakan hukum dan riset ilmiah."),
        ("Kesiapan Implementasi (Production Ready)", "Sudah terhubung antara web app responsif, backend FastAPI, serta arsitektur yang siap diubah menjadi aplikasi Android via Capacitor."),
        ("Dampak Sosial Nyata", "Melindungi masyarakat dari maraknya penipuan telepon vishing dan manipulasi media sintetis di era kecerdasan buatan.")
    ]

    for title, desc in points:
        p_pt = tf8.add_paragraph()
        p_pt.text = f"•  {title}: {desc}"
        p_pt.font.size = Pt(13)
        p_pt.font.color.rgb = RGBColor(226, 232, 240)
        p_pt.space_before = Pt(8)

    p_close = tf8.add_paragraph()
    p_close.text = "Terima Kasih  |  Sesi Tanya Jawab (Q&A)"
    p_close.font.size = Pt(16)
    p_close.font.bold = True
    p_close.font.color.rgb = RGBColor(147, 197, 253)
    p_close.space_before = Pt(24)

    # Save presentation
    prs.save(output_path)
    print(f"Presentation saved successfully to: {output_path}")

if __name__ == "__main__":
    out_file = r"C:\Jasim\BKI\ai detection\ai-detector-suara\GuardiVoice_Presentasi_BAMBS.pptx"
    create_guardivoice_presentation(out_file)
