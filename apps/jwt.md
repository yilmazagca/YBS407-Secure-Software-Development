Bu kod, JWT (JSON Web Token) tabanlı kimlik doğrulama işleminin küçük bir örneğidir. Web sitelerinde ve API'lerde "bu kullanıcı giriş yapmış mı?" sorusunu, her istekte veritabanına gitmeden cevaplamak için kullanılır.
Mantık (günlük hayat benzetmesi)

Konser bileti gibi düşünün: Girişte kimliğinizi bir kez kontrol ederler, size üzerinde mühür olan bir bilek bandı verirler. Sonraki girişlerde sadece bandın mührüne bakarlar. JWT de bu banttır, SECRET_KEY ise mühürdür.
Kodda olanlar adım adım

1. create_jwt(user_id): token üretme (genelde kullanıcı giriş yaptıktan sonra çalışır)

    payload hazırlanır: kullanıcı ID'si (user_id) ve bitiş zamanı (exp, şu andan 1 saat sonra).

    jwt.encode(...) bu payload'u SECRET_KEY ile HS256 algoritması kullanarak imzalar.

    Sonuç şöyle üç parçalı bir metindir: xxxxx.yyyyy.zzzzz (başlık . içerik . imza). Bu token istemciye (tarayıcı/mobil uygulama) gönderilir.

2. verify_jwt(token): token doğrulama (istemci her istekte token'ı geri gönderir)

    jwt.decode(...) şunları kontrol eder:

        İmza doğru mu? (Token'ın içeriği değiştirilmiş mi, başkası mı üretmiş?)

        Süresi dolmuş mu? (exp)

    Sorun yoksa payload'u açıp user_id'yi döndürür.

    Süre dolmuşsa ExpiredSignatureError, imza bozuksa veya token geçersizse InvalidTokenError yakalanır ve hata mesajı verilir.

3. Test bölümü

    create_jwt(105) ile ID'si 105 olan kullanıcı için token üretilir ve ekrana yazılır.

    verify_jwt(ornek_token) ile aynı token doğrulanır ve "Doğrulama başarılı. Kullanıcı ID: 105" çıktısı alınır.

Tipik kullanım akışı

    Kullanıcı kullanıcı adı/şifre ile giriş yapar.

    Sunucu create_jwt ile token üretip kullanıcıya verir.

    Kullanıcı sonraki isteklerde token'ı gönderir (genelde Authorization: Bearer <token> başlığıyla).

    Sunucu verify_jwt ile token'ı kontrol eder, geçerliyse isteği kullanıcı adına işler.

*Önemli not*

Bu kod sadece token üretme ve doğrulama kısmıdır. Şifre kontrolü, kullanıcı veritabanı, web sunucusu (Flask/FastAPI vb.) gibi parçalar yoktur. Yani eğitim amaçlı bir iskelettir.

### Koddaki Zafiyetler

    * SECRET_KEY hardcoded – Kaynak kodda saklanmış, deposita commit edilirse bütün tokenlar tehlikede

    * Weak SECRET_KEY – Çok basit, brute force atakına karşı zayıf

    * verify_jwt hatalı dönüş değeri – String döndüğü için if verified_user_id: her zaman True olur (hata olsa bile)

    * Payload şifreli değil – JWT'nin payload kısmı sadece base64, şifreli değil. Hassas bilgi koymak güvenli değil

    * Token iptal mekanizması yok – Logout sonrası token'ı kullanmaya devam edebilir

    * Error handling zayıf – Debug mesajları üretim kodunda bilgi sızıntısına neden olabilir