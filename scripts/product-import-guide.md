# 商品自動匯入腳本使用教學

主要使用這個檔案：

```cmd
scripts\run-product-import.cmd
```

## 1. 準備商品資料檔

商品資料檔可以使用 `.csv` 或 `.xlsx`。

建議欄位：

```csv
category,product,images,category_slug,product_slug
大瓶系列,百威啤酒,budweiser.png,big-bottles,budweiser
大瓶系列,海尼根,heineken.png,big-bottles,heineken
```

欄位說明：

- `category`：分類名稱
- `product`：商品名稱
- `images`：圖片檔名，可留空
- `category_slug`：分類資料夾名稱，建議用英文或數字
- `product_slug`：商品資料夾名稱，建議用英文或數字

如果一個商品有多張圖片，請用分號 `;` 分隔：

```csv
category,product,images,category_slug,product_slug
大瓶系列,百威啤酒,budweiser-1.png;budweiser-2.png,big-bottles,budweiser
```

## 2. 準備商品圖片

如果商品有圖片，請把圖片集中放在一個資料夾，例如：

```text
product-images
├─ budweiser.png
├─ heineken.png
```

如果商品資料檔的 `images` 欄位是空的，就不需要準備圖片資料夾。

## 3. 執行匯入腳本

在專案根目錄執行：

```cmd
scripts\run-product-import.cmd
```

腳本會依序詢問：

```text
Source CSV or Excel file path:
```

輸入商品資料檔路徑，例如：

```text
C:\Users\chunchun\Desktop\products.csv
```

如果商品資料檔放在專案根目錄，也可以輸入：

```text
products.csv
```

接著會詢問：

```text
Image folder path (optional):
```

如果圖片放在 `product-images`，輸入：

```text
product-images
```

如果沒有圖片，直接按 Enter。

接著會詢問：

```text
Dry run first? (Y/N, default Y):
```

第一次建議直接按 Enter，或輸入：

```text
Y
```

Dry Run 只會預覽，不會真的建立檔案。

確認輸出路徑正確後，再重新執行一次，這次輸入：

```text
N
```

才會正式匯入。

## 4. 匯入後的位置

商品會匯入到：

```text
public_html\user\pages\02.all_produts
```

產生的結構範例：

```text
02.all_produts
├─ 01.big-bottles
│  ├─ blog.md
│  ├─ 01.budweiser
│  │  ├─ item.md
│  │  └─ budweiser.png
│  ├─ 02.heineken
│  │  ├─ item.md
│  │  └─ heineken.png
```

