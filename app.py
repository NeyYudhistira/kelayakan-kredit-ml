from flask import Flask, render_template, request
import numpy as np
import joblib
import os

app = Flask(__name__)

# Load model, scaler, dan encoder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "model")

rf_model      = joblib.load(os.path.join(MODEL_DIR, "random_forest_model.pkl"))
scaler        = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
label_encoders = joblib.load(os.path.join(MODEL_DIR, "label_encoders.pkl"))


def encode_kategori(col, value):
    """Encode nilai kategorikal menggunakan LabelEncoder yang sudah dilatih."""
    le = label_encoders.get(col)
    if le is None:
        raise ValueError(f"Encoder untuk '{col}' tidak ditemukan.")
    if value not in le.classes_:
        # Fallback ke kelas pertama jika nilai tidak dikenal
        value = le.classes_[0]
    return int(le.transform([value])[0])


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        # ── Ambil input dari form ──────────────────────────────────────────
        usia                  = float(request.form["usia"])
        status_pekerjaan      = request.form["status_pekerjaan"]
        lama_bekerja          = float(request.form["lama_bekerja_tahun"])
        pendapatan_tahunan    = float(request.form["pendapatan_tahunan"])
        skor_kredit           = float(request.form["skor_kredit"])
        lama_riwayat_kredit   = float(request.form["lama_riwayat_kredit_tahun"])
        aset_tabungan         = float(request.form["aset_tabungan"])
        hutang_saat_ini       = float(request.form["hutang_saat_ini"])
        gagal_bayar           = int(request.form["gagal_bayar_tercatat"])
        tunggakan             = int(request.form["tunggakan_2thn_terakhir"])
        catatan_negatif       = int(request.form["catatan_negatif"])
        tipe_produk           = request.form["tipe_produk"]
        tujuan_pinjaman       = request.form["tujuan_pinjaman"]
        jumlah_pinjaman       = float(request.form["jumlah_pinjaman"])
        suku_bunga            = float(request.form["suku_bunga"])

        # ── Hitung rasio otomatis ──────────────────────────────────────────
        rasio_hutang          = hutang_saat_ini / pendapatan_tahunan if pendapatan_tahunan else 0
        rasio_pinjaman        = jumlah_pinjaman / pendapatan_tahunan if pendapatan_tahunan else 0
        cicilan_per_tahun     = jumlah_pinjaman * (suku_bunga / 100)
        rasio_pembayaran      = cicilan_per_tahun / pendapatan_tahunan if pendapatan_tahunan else 0

        # ── Encode kategorikal ─────────────────────────────────────────────
        enc_status_pekerjaan  = encode_kategori("status_pekerjaan", status_pekerjaan)
        enc_tipe_produk       = encode_kategori("tipe_produk", tipe_produk)
        enc_tujuan_pinjaman   = encode_kategori("tujuan_pinjaman", tujuan_pinjaman)

        # ── Susun fitur (urutan harus sama dengan training) ───────────────
        # Urutan: usia, status_pekerjaan, lama_bekerja_tahun, pendapatan_tahunan,
        #         skor_kredit, lama_riwayat_kredit_tahun, aset_tabungan,
        #         hutang_saat_ini, gagal_bayar_tercatat, tunggakan_2thn_terakhir,
        #         catatan_negatif, tipe_produk, tujuan_pinjaman, jumlah_pinjaman,
        #         suku_bunga, rasio_hutang_terhadap_pendapatan,
        #         rasio_pinjaman_terhadap_pendapatan, rasio_pembayaran_terhadap_pendapatan
        features = np.array([[
            usia,
            enc_status_pekerjaan,
            lama_bekerja,
            pendapatan_tahunan,
            skor_kredit,
            lama_riwayat_kredit,
            aset_tabungan,
            hutang_saat_ini,
            gagal_bayar,
            tunggakan,
            catatan_negatif,
            enc_tipe_produk,
            enc_tujuan_pinjaman,
            jumlah_pinjaman,
            suku_bunga,
            rasio_hutang,
            rasio_pinjaman,
            rasio_pembayaran,
        ]])

        # ── Scaling & Prediksi ─────────────────────────────────────────────
        features_scaled = scaler.transform(features)
        prediction_num  = rf_model.predict(features_scaled)[0]
        proba           = rf_model.predict_proba(features_scaled)[0]
        confidence      = round(float(max(proba)) * 100, 2)

        # 1 = Layak, 0 = Tidak Layak
        status = "Layak" if prediction_num == 1 else "Tidak Layak"

        # ── Data input untuk ditampilkan di result.html ────────────────────
        input_data = {
            "usia": int(usia),
            "status_pekerjaan": status_pekerjaan,
            "lama_bekerja_tahun": lama_bekerja,
            "pendapatan_tahunan": f"Rp {int(pendapatan_tahunan):,}".replace(",", "."),
            "skor_kredit": int(skor_kredit),
            "lama_riwayat_kredit_tahun": lama_riwayat_kredit,
            "aset_tabungan": f"Rp {int(aset_tabungan):,}".replace(",", "."),
            "hutang_saat_ini": f"Rp {int(hutang_saat_ini):,}".replace(",", "."),
            "gagal_bayar_tercatat": gagal_bayar,
            "tunggakan_2thn_terakhir": tunggakan,
            "catatan_negatif": catatan_negatif,
            "tipe_produk": tipe_produk,
            "tujuan_pinjaman": tujuan_pinjaman,
            "jumlah_pinjaman": f"Rp {int(jumlah_pinjaman):,}".replace(",", "."),
            "suku_bunga": suku_bunga,
            "rasio_hutang_terhadap_pendapatan": rasio_hutang,
            "rasio_pinjaman_terhadap_pendapatan": rasio_pinjaman,
            "rasio_pembayaran_terhadap_pendapatan": rasio_pembayaran,
        }

        return render_template(
            "result.html",
            prediction=status,
            confidence=confidence,
            input_data=input_data,
        )

    except Exception as e:
        return render_template(
            "result.html",
            prediction=None,
            error=str(e),
            input_data={},
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
