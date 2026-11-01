---
alan: eee
---
# Ders kartı: Linear Algebra · Lineer (Doğrusal) Cebir

Genel ders bilgisi (kişisel değil). İlerleme ve kişisel notlar kullanıcının proje klasöründe `dersler/linear-algebra/hafiza.md`.

## Kaynak önceliği
yüklenen ders notu / çıkmış soru > ders kitabı > genel bilgi (ayar A4)

Kitap: Anton & Rorres, *Elementary Linear Algebra*. Yardımcı: Leon, *Linear Algebra with Applications*. Ders Türkçe işlenir; Türkçe terim esastır, İngilizcesi parantezde durur (ayar C3). Bölüm numaraları Anton'un 10.–12. basımlarında aynıdır; alt başlık numarası basıma göre kayabilir.

## Müfredat sırası (konu → Anton bölümü)
| # | Konu | Kitap bölümü |
|---|---|---|
| 1 | Doğrusal denklem sistemleri, temel satır işlemleri | 1 Systems of Linear Equations and Matrices |
| 2 | Gauss ve Gauss–Jordan yok etme | 1 |
| 3 | Matrisler, temel işlemler ve kurallar | 1 |
| 4 | Ters matris ve bulma yöntemleri | 1 |
| 5 | Determinant: tanım, satır indirgeme, kofaktör açılımı | 2 Determinants |
| 6 | Determinant özellikleri | 2 |
| 7 | 2 boyutta vektörler, vektör çarpımları, doğru ve düzlem | 3 Euclidean Vector Spaces |
| 8 | 3 boyutta vektörler | 3 |
| 9 | Öklid vektör uzayı, dönüşümler | 3 ve 4 General Vector Spaces ($\mathbb{R}^n$ kısmı, matris dönüşümleri) |
| 10 | İç çarpım uzayları, ortonormal bazlar | 6 Inner Product Spaces |
| 11 | Özdeğer ve özvektör | 5 Eigenvalues and Eigenvectors |
| 12 | Köşegenleştirme ve ortogonal dönüşüm | 5 ve 7 Diagonalization and Quadratic Forms |
| 13 | Doğrusal dönüşümler: çekirdek, aralık | 8 General Linear Transformations |
| 14 | Ters dönüşümler, dönüşümün matris hali | 8 |

LU ayrışımı yüklenen ders notunda varsa anlatılır (Anton: sayısal yöntemler bölümündeki LU-decompositions); notta yoksa yalnız kısa "İleriden bir ipucu".

## Konu tipleri (ayar E3)
| Konu | Tip |
|---|---|
| Doğrusal sistemler, Gauss/Gauss–Jordan | hesap (algoritma) |
| Matris işlemleri, ters matris | hesap + kural |
| Determinant ve özellikleri | hesap + kavram |
| Vektörler, nokta ve vektör çarpımı, doğru ve düzlem | hesap + geometri |
| Öklid uzayı, doğrusal dönüşümler | kavram + hesap |
| İç çarpım uzayı, ortonormal baz (Gram–Schmidt) | hesap + kavram |
| Özdeğer, özvektör, köşegenleştirme | hesap |
| Çekirdek, aralık, dönüşümün matrisi | kavram + hesap |

## Notasyon ve birim
- Matris $A=[a_{ij}]$, `bmatrix` ile yazılır; vektör kalın $\mathbf{u}$ ya da $\vec{u}$ (yüklenen not hangisini kullanıyorsa o). Birim yoktur; boyutlar ($m\times n$) her zaman yazılır.
- Satır işlemleri (yüklenen notta farklıysa onun gösterimi): $R_i \leftrightarrow R_j$, $cR_i \to R_i$, $R_i + cR_j \to R_i$. Genişletilmiş matris $[A\mid\mathbf{b}]$.
- Determinant $\det(A)$ ya da $|A|$; kofaktör $C_{ij}=(-1)^{i+j}M_{ij}$.
- Nokta çarpım $\mathbf{u}\cdot\mathbf{v}$, norm $\|\mathbf{u}\|$, vektör çarpımı $\mathbf{u}\times\mathbf{v}$ (yalnız $\mathbb{R}^3$). Özdeğer denklemi $\det(\lambda I - A)=0$.
- Adım adım hesap satır satır yazılır; her satır işlemi işlemin adıyla birlikte gösterilir (matrisler arası ok değil, ayrı satır).

## Sık tuzaklar
- Matris çarpımı değişmeli değildir; $(AB)^{-1}=B^{-1}A^{-1}$ ve $(AB)^T=B^TA^T$ (sıra tersine döner).
- $\det(A+B)\neq\det A+\det B$; $\det(kA)=k^{n}\det A$; satır değiştirme determinantın işaretini değiştirir, bir satırı $k$ ile çarpmak determinantı $k$ ile çarpar.
- Gauss–Jordan'da satır işleminde işaret hatası ve sıfır olmayan pivot seçimi; indirgenmiş eşelon formda pivot sütunları dışında kalan serbest değişkenler.
- Kofaktör açılımında $(-1)^{i+j}$ işaret deseni.
- Özvektör sıfır vektör olamaz; cebirsel ve geometrik katlılık farkı; $n$ tane doğrusal bağımsız özvektör yoksa köşegenleştirilemez.
- Ortogonal ile ortonormal ayrı: ortonormalde ayrıca norm 1.
- Çekirdek tanım kümesinin altuzayı, aralık değer kümesinin altuzayıdır; $\operatorname{rank}+\operatorname{nullity}=n$ ($n$ sütun sayısı).
- Vektör çarpımı değişmeli değil, ters değişmelidir ($\mathbf{u}\times\mathbf{v}=-\mathbf{v}\times\mathbf{u}$); doğru ve düzlem denkleminde yön vektörü ile normal vektörü karıştırmak.

## Uygulama örnek havuzu
Devrede düğüm/göz denklemlerinin doğrusal sistem olarak kurulup Gauss ile çözülmesi, ölçüm verisine en küçük kareler doğrusu, dönme matrisleriyle koordinat dönüşümü (robotik, görüntü), özdeğerlerle salınım kipleri ve kararlılık, iç çarpımla sinyal benzerliği (korelasyon), ortogonal ayrışım (Fourier fikrinin öncülü).
