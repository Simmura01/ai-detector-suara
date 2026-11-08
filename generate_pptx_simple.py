import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_simplified_presentation(output_path):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Palet Warna Ramah, Modern & Profesional
    DARK_BG = RGBColor(15, 23, 42)       # Slate 900
    LIGHT_BG = RGBColor(248, 250, 252)   # Slate 50
    CARD_BG = RGBColor(255, 255, 255)    # White
    CARD_BORDER = RGBColor(226, 232, 240)# Slate 200
    PRIMARY_BLUE = RGBColor(37, 99, 235) # Blue 600
    ACCENT_CYAN = RGBColor(14, 165, 233) # Sky 500
    TEXT_DARK = RGBColor(15, 23, 42)     # Slate 900
    TEXT_MUTED = RGBColor(100, 116, 139) # Slate 500
    TEXT_LIGHT = RGBColor(241, 245, 249) # Slate 100
    EMERALD = RGBColor(16, 185, 129)     # Emerald 500
    RED_ACCENT = RGBColor(239, 68, 68)   # Red 500
    PURPLE_ACCENT = RGBColor(168, 85, 247)# Purple 500

    def add_bg(slide, color):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_header(slide, badge_text, title_text, category_text="GuardiVoice • Detektor Suara AI"):
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.4), Inches(11.733), Inches(0.04))
        line.fill.solid()
        line.fill.fore_color.rgb = PRIMARY_BLUE
        line.line.fill.background()

        tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.55), Inches(11.733), Inches(0.95))
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
    # SLIDE 1: COVER SLIDE (Mudah Dipahami, Santai & Keren)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    add_bg(s1, DARK_BG)

    dec = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(1.6), Inches(0.1), Inches(4.3))
    dec.fill.solid()
    dec.fill.fore_color.rgb = PRIMARY_BLUE
    dec.line.fill.background()

    tb1 = s1.shapes.add_textbox(Inches(1.4), Inches(1.6), Inches(10.5), Inches(4.3))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "INOVASI TEKNOLOGI DETEKSI KEASLIAN SUARA (IYSA / BKI)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE
    p.space_after = Pt(12)

    p2 = tf1.add_paragraph()
    p2.text = "GuardiVoice"
    p2.font.size = Pt(46)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_LIGHT

    p3 = tf1.add_paragraph()
    p3.text = "Membedakan Suara Manusia Asli vs Suara Robot AI"
    p3.font.size = Pt(24)
    p3.font.bold = True
    p3.font.color.rgb = RGBColor(147, 197, 253)
    p3.space_before = Pt(6)
    p3.space_after = Pt(16)

    p4 = tf1.add_paragraph()
    p4.text = "Metode Pendeteksi Berbasis Ciri Fisik Akustik Biologis: Menangkap Perbedaan Alami Antara Getaran Pita Suara Manusia dan Suara Buatan Komputer."
    p4.font.size = Pt(14)
    p4.font.color.rgb = RGBColor(203, 213, 225)
    p4.space_after = Pt(28)

    p5 = tf1.add_paragraph()
    p5.text = "Disusun oleh: Jasim & Tim Peneliti  |  Kategori: Kecerdasan Buatan & Pemrosesan Sinyal Suara"
    p5.font.size = Pt(11)
    p5.font.color.rgb = RGBColor(148, 163, 184)

    # =========================================================================
    # SLIDE 2: LATAR BELAKANG (Analogi Mudah & Nyata)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_bg(s2, LIGHT_BG)
    add_header(s2, "Bagian 01 • Masalah", "Ketika Suara Manusia Mulai Bisa 'Ditiru' Oleh Mesin")

    card_w = Inches(3.64)
    gap = Inches(0.4)
    left_start = Inches(0.8)
    top_pos = Inches(1.8)
    card_h = Inches(4.8)

    points_s2 = [
        ("01 • TREN SAAT INI", "Cukup Rekaman 3 Detik", 
         "Sekarang AI sangat canggih. Cukup ambil potongan suara seseorang dari video TikTok atau WhatsApp 3 detik, komputer sudah bisa menduplikasi gaya bicara orang tersebut secara instan.",
         PRIMARY_BLUE),
        ("02 • BAHAYA NYATA", "Penipuan Telepon & Keluarga", 
         "Banyak penipu memakai kloning suara untuk menelepon orang tua, mengaku anaknya celaka atau minta uang darurat. Korban percaya karena suaranya terdengar sangat mirip aslinya.",
         RED_ACCENT),
        ("03 • MENGAPA SULIT?", "Telinga Manusia Terkecoh", 
         "Telinga kita tidak bisa lagi membedakan mana rekaman asli dan mana suara buatan AI. Kita butuh alat bantu ilmiah yang bisa 'melihat' getaran suara sampai ke tingkat gelombang terkecil.",
         RGBColor(217, 119, 6))
    ]

    for i, (badge, title, desc, col) in enumerate(points_s2):
        cx = left_start + i * (card_w + gap)
        add_card(s2, cx, top_pos, card_w, card_h)
        
        pill = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, top_pos, card_w, Inches(0.08))
        pill.fill.solid()
        pill.fill.fore_color.rgb = col
        pill.line.fill.background()

        tb = s2.shapes.add_textbox(cx + Inches(0.3), top_pos + Inches(0.35), card_w - Inches(0.6), card_h - Inches(0.7))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = badge
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = col
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
    # SLIDE 3: SOLUSI UMUM (Konsep Logika Biologis vs Mesin)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_bg(s3, LIGHT_BG)
    add_header(s3, "Bagian 02 • Ide Solusi", "Solusi: Memeriksa Tanda-Tanda Fisik Suara Manusia")

    points_s3 = [
        ("PENDEKATAN KITA", "Bukan Menebak, Tapi Menguji", 
         "Kebanyakan sistem AI hanya menebak tanpa alasan jelas. Pendekatan kami berbeda: kami memeriksa apakah suara tersebut mematuhi cara kerja organ biologis manusia (paru-paru & pita suara).",
         PRIMARY_BLUE),
        ("ANALOGI DOKTER", "Seperti Dokter THT Digital", 
         "Bayangkan seperti tes kesehatan suara. Sistem memeriksa denyut getaran, hembusan napas, dan pantulan tenggorokan. Mesin komputer tidak punya paru-paru, jadi selalu meninggalkan jejak palsu.",
         EMERALD),
        ("FLEKSIBEL & CEPAT", "Algoritma Terbuka & Ringan", 
         "Sistem dibuat fleksibel dan modular sehingga mudah dikembangkan atau diganti model algoritmanya. Proses pemeriksaannya sangat cepat bahkan bisa jalan di smartphone biasa.",
         PURPLE_ACCENT)
    ]

    for i, (badge, title, desc, col) in enumerate(points_s3):
        cx = left_start + i * (card_w + gap)
        add_card(s3, cx, top_pos, card_w, card_h)
        
        pill = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, top_pos, card_w, Inches(0.08))
        pill.fill.solid()
        pill.fill.fore_color.rgb = col
        pill.line.fill.background()

        tb = s3.shapes.add_textbox(cx + Inches(0.3), top_pos + Inches(0.35), card_w - Inches(0.6), card_h - Inches(0.7))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = badge
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = col
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
    # SLIDE 4: 4 CIRI FISIK SUARA (Bahasa Mudah & Analogi)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_bg(s4, LIGHT_BG)
    add_header(s4, "Bagian 03 • Parameter Fisik", "4 Ciri Kunci yang Membedakan Manusia vs AI")

    b_easy = [
        ("CIRI 01 • NADA SUARA", "Kelenturan Nada (Pitch Range)", 
         "Analogi: Roller Coaster Nada", 
         "Manusia kalau bicara nadanya naik-turun secara lentur dan ekspresif. Suara robot AI biasanya cenderung kaku, datar, dan rentang nadanya lebih sempit.",
         PRIMARY_BLUE),
        ("CIRI 02 • KEKUATAN GETARAN", "Getaran Halus Suara (Shimmer)", 
         "Analogi: Kestabilan Denyut", 
         "Pita suara manusia bergetar dengan sangat stabil. AI yang dibuat dari rumus matematika sering memiliki 'lonjakan kecil' mikro yang tidak wajar pada kekerasan suaranya.",
         RGBColor(217, 119, 6)),
        ("CIRI 03 • NAFAS & UDARA", "Hembusan Napas (Harmonic-to-Noise)", 
         "Analogi: Hembusan Alami Paru-paru", 
         "Saat manusia berbicara, selalu ada hembusan udara alami dari paru-paru. AI tidak bernapas, sehingga suara buatannya sering memiliki dengung frekuensi yang aneh.",
         EMERALD),
        ("CIRI 04 • BENTUK MULUT", "Pantulan Rongga Suara (MFCC)", 
         "Analogi: Gema di Ruang Tertutup", 
         "Bentuk lidah, bibir, dan tenggorokan manusia memantulkan suara dengan rumus tertentu. Mesin AI sangat sering gagal meniru pantulan rongga tenggorokan ini secara konsisten.",
         PURPLE_ACCENT)
    ]

    gw = Inches(5.65)
    gh = Inches(2.25)
    g_x = [Inches(0.8), Inches(6.88)]
    g_y = [Inches(1.8), Inches(4.35)]

    for idx, (badge, title, ana, desc, col) in enumerate(b_easy):
        col_idx = idx % 2
        row_idx = idx // 2
        bx = g_x[col_idx]
        by = g_y[row_idx]
        
        add_card(s4, bx, by, gw, gh)
        
        bar = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, bx, by, Inches(0.1), gh)
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tb = s4.shapes.add_textbox(bx + Inches(0.25), by + Inches(0.18), gw - Inches(0.45), gh - Inches(0.3))
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
        p3.text = ana
        p3.font.size = Pt(11)
        p3.font.bold = True
        p3.font.color.rgb = col
        p3.space_before = Pt(2)
        p3.space_after = Pt(4)

        p4 = tf.add_paragraph()
        p4.text = desc
        p4.font.size = Pt(10.5)
        p4.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 5: CARA KERJA SISTEM (Langkah Simpel)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_bg(s5, LIGHT_BG)
    add_header(s5, "Bagian 04 • Cara Kerja", "Bagaimana Aplikasi Memeriksa Suara Pengguna?")

    flow_steps = [
        ("LANGKAH 1", "Rekam atau Upload", 
         "Pengguna bisa menekan tombol rekam mikrofon atau mengunggah rekaman suara (.wav / .mp3) yang mencurigakan.",
         "Sinyal Suara Masuk"),
        ("LANGKAH 2", "Pecah Gelombang", 
         "Komputer memecah rekaman menjadi gelombang frekuensi untuk melihat detail getaran yang tak terlihat mata.",
         "Analisis Spektrum Audio"),
        ("LANGKAH 3", "Cek Batas Biologis", 
         "Sistem mencocokkan nilai 4 ciri suara tadi: Apakah nadanya wajar? Apakah ada napasnya? Apakah getarannya manusiawi?",
         "Pencocokan Ciri Fisik"),
        ("LANGKAH 4", "Hasil & Skor", 
         "Aplikasi langsung menampilkan label jelas: 'Suara Manusia Asli' atau 'Suara Sintetis AI' beserta tingkat keyakinannya.",
         "Vonis Cepat & Jelas")
    ]

    sw = Inches(2.72)
    sgap = Inches(0.28)
    s_top = Inches(1.8)
    s_h = Inches(4.8)

    for i, (tag, title, desc, sub) in enumerate(flow_steps):
        sx = Inches(0.8) + i * (sw + sgap)
        add_card(s5, sx, s_top, sw, s_h)

        tag_box = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, sx, s_top, sw, Inches(0.5))
        tag_box.fill.solid()
        tag_box.fill.fore_color.rgb = PRIMARY_BLUE
        tag_box.line.fill.background()

        tb_tag = s5.shapes.add_textbox(sx, s_top + Inches(0.1), sw, Inches(0.3))
        p = tb_tag.text_frame.paragraphs[0]
        p.text = tag
        p.alignment = PP_ALIGN.CENTER
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_LIGHT

        tb_body = s5.shapes.add_textbox(sx + Inches(0.2), s_top + Inches(0.65), sw - Inches(0.4), s_h - Inches(0.8))
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

        p3 = tf.add_paragraph()
        p3.text = sub
        p3.font.size = Pt(9.5)
        p3.font.bold = True
        p3.font.color.rgb = PRIMARY_BLUE

    # =========================================================================
    # SLIDE 6: TAMPILAN APLIKASI WEB (Sederhana untuk Pengguna)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_bg(s6, LIGHT_BG)
    add_header(s6, "Bagian 05 • Antarmuka", "Desain Tampilan Web: Bersih, Cepat & Tanpa Rumit")

    ui_points = [
        ("01 • MUDAH DIGUNAKAN", "Tinggal Rekam atau Seret File",
         "Dibuat sederhana tanpa tombol yang membingungkan. Pengguna awam cukup menekan tombol 'Rekam Suara' di HP atau mengunggah file rekaman dari galeri."),
        ("02 • HASIL SEPERTI SPEEDOMETER", "Vonis Jelas & Persentase Skor",
         "Alih-alih rumus rumit yang memusingkan, hasil langsung terlihat: Kotak Hijau untuk 'Suara Manusia Asli' dan Kotak Merah jika terdeteksi 'Suara Robot AI'."),
        ("03 • DETAIL FORENSIK OPSIONAL", "Bukti Bisa Dibuka Kapan Saja",
         "Jika ingin memeriksa alasannya secara ilmiah (misalnya untuk juri lomba atau pihak berwenang), ada menu 'Analisis Mendalam' yang bisa dibuka dengan satu kali klik."),
        ("04 • SIAP JADI APLIKASI HP", "Bisa Diakses di Web & Smartphone",
         "Desain responsif yang nyaman dibuka di layar HP Android dan iPhone, serta siap dikonversi menjadi aplikasi mandiri di masa depan.")
    ]

    card_h_ui = Inches(2.25)
    for idx, (badge, title, desc) in enumerate(ui_points):
        c_col = idx % 2
        c_row = idx // 2
        bx = g_x[c_col]
        by = g_y[c_row]
        
        add_card(s6, bx, by, gw, card_h_ui)

        tb = s6.shapes.add_textbox(bx + Inches(0.3), by + Inches(0.2), gw - Inches(0.6), card_h_ui - Inches(0.35))
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
    # SLIDE 7: KESIMPULAN & POTENSI MASA DEPAN (Closing Slide)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_bg(s7, DARK_BG)

    tb7 = s7.shapes.add_textbox(Inches(1.0), Inches(0.9), Inches(11.333), Inches(5.8))
    tf7 = tb7.text_frame
    tf7.word_wrap = True

    p = tf7.paragraphs[0]
    p.text = "KESIMPULAN & RENCANA PENGEMBANGAN"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE
    p.space_after = Pt(8)

    p2 = tf7.add_paragraph()
    p2.text = "Inovasi Proteksi Digital yang Terbuka & Nyata"
    p2.font.size = Pt(26)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_LIGHT
    p2.space_after = Pt(20)

    points_close = [
        ("Bisa Dijelaskan Ilmiah", "Tidak sekadar menebak; keputusan diambil dari pemeriksaan karakteristik fisik pita suara yang nyata."),
        ("Masih Tahap Prototype", "Sistem dirancang modular sehingga ke depan dapat diperkaya dengan algoritma atau batas fisik baru yang lebih canggih."),
        ("Manfaat Bagi Masyarakat", "Bisa menjadi benteng perlindungan pertama bagi orang tua, sekolah, dan masyarakat dari penipuan telepon vishing."),
        ("Rencana Lanjutan", "Mengintegrasikan pendeteksi langsung ke aplikasi telepon dan memperbanyak ragam aksen bahasa daerah di Indonesia.")
    ]

    for title, desc in points_close:
        p_pt = tf7.add_paragraph()
        p_pt.text = f"•  {title}: {desc}"
        p_pt.font.size = Pt(13)
        p_pt.font.color.rgb = RGBColor(226, 232, 240)
        p_pt.space_before = Pt(8)

    p_close = tf7.add_paragraph()
    p_close.text = "Terima Kasih!  |  Sesi Tanya Jawab"
    p_close.font.size = Pt(16)
    p_close.font.bold = True
    p_close.font.color.rgb = RGBColor(147, 197, 253)
    p_close.space_before = Pt(24)

    prs.save(output_path)
    print(f"Simplified Presentation saved successfully to: {output_path}")

if __name__ == "__main__":
    out_file = r"C:\Jasim\BKI\ai detection\ai-detector-suara\GuardiVoice_Presentasi_BAMBS.pptx"
    create_simplified_presentation(out_file)
