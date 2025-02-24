# usom-ioc-fetcher

Bu proje, Türkiye Cumhuriyeti Ulusal Siber Olaylara Müdahale Merkezi (USOM) tarafından sağlanan IoC (Indicators of Compromise - Tehdit Göstergeleri) verilerini çeken ve belirtilen tarihe göre filtreleyebilen bir Python scriptidir. Apache Airflow ile periyodik ve otomatik çalıştırılmak üzere tasarlanmıştır.

# Özellikler:

USOM üzerinden IoC verilerini sayfa sayfa çeker ve yerel JSON dosyası olarak kaydeder.
API'nin limitlerine takıldığında otomatik olarak bekleyip tekrar dener.
Belirlenen tarihten sonraki IoC verilerini ayrı bir dosyaya kaydeder.
Airflow kullanılarak periyodik olarak çalıştırılır.

# Kullanılan Teknolojiler:

Python 3.x
Apache Airflow
requests kütüphanesi

# Kurulum:

Öncelikle GitHub üzerinden proje deposunu kendi bilgisayarınıza klonlayın.

git clone https://github.com/kullaniciadi/usom-ioc-fetcher.git cd usom-ioc-fetcher

Gerekli Python kütüphanelerini yükleyin:

pip install requests apache-airflow

Airflow'un DAG klasörüne kod dosyasını kopyalayın. Genellikle bu dizin ~/airflow/dags/ şeklindedir:

cp usom_ioc_fetcher.py ~/airflow/dags/

Airflow web arayüzüne giderek DAG'ı aktifleştirin. DAG günlük çalışmak üzere ayarlanmıştır. Çalışma periyodunu değiştirmek isterseniz kodun içindeki 'schedule' parametresini güncelleyebilirsiniz.

Oluşturulan Dosyalar: Kod çalıştırıldığında masaüstünde (Desktop) iki JSON dosyası oluşacaktır:

Tüm IoC verileri için: output_ioc.json
Tarih filtresi uygulanmış IoC verileri için: filtered_output_ioc.json
Bu dosya yollarını değiştirmek için kod içerisindeki ilgili kısımları düzenleyebilirsiniz.

Lisans: Bu proje MIT lisansı ile lisanslanmıştır. İstediğiniz gibi kullanabilir, değiştirebilir ve dağıtabilirsiniz. Detaylar için LICENSE dosyasını inceleyebilirsiniz.
