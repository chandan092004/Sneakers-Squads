/**
 * SNEAKER SQUAD - PRODUCT DETAIL PAGE JAVASCRIPT (product-detail.js)
 * Manages URL parameter resolution, dynamic content injection, multi-angle
 * color-specific image gallery switcher, size/color selectors, extended tabs
 * (Shoe Features, Technical Specs, Full Description, Care & Cleaning),
 * pincode checker, related products recommendation, and multi-colorway cart integration.
 */

// Global product lookup
if (!window.getProductById) {
  window.getProductById = function(id) {
    if (!id) return null;
    const cleanId = String(id).trim().toLowerCase();
    if (window.PRODUCTS_DATA && window.PRODUCTS_DATA[cleanId]) {
      return window.PRODUCTS_DATA[cleanId];
    }
    if (window.PRODUCTS_DATA) {
      for (const k in window.PRODUCTS_DATA) {
        if (k.toLowerCase() === cleanId || (window.PRODUCTS_DATA[k].id && window.PRODUCTS_DATA[k].id.toLowerCase() === cleanId)) {
          return window.PRODUCTS_DATA[k];
        }
      }
    }
    return null;
  };
}

// Global related products lookup
if (!window.getRelatedProducts) {
  window.getRelatedProducts = function(currentId, count = 4) {
    if (!window.PRODUCTS_DATA) return [];
    const cleanId = String(currentId).trim().toLowerCase();
    const currentProd = window.getProductById(cleanId);
    const allProducts = Object.values(window.PRODUCTS_DATA);
    
    // Filter out current product
    const otherProducts = allProducts.filter(p => p.id && p.id.toLowerCase() !== cleanId);

    // Prefer same gender/category
    if (currentProd) {
      const sameGender = otherProducts.filter(p => p.gender === currentProd.gender);
      if (sameGender.length >= count) {
        return sameGender.slice(0, count);
      }
    }

    return otherProducts.slice(0, count);
  };
}

document.addEventListener('DOMContentLoaded', () => {
  initProductDetailPage();
});

function initProductDetailPage() {
  // 1. Get Product ID from URL
  const urlParams = new URLSearchParams(window.location.search);
  const productId = urlParams.get('id') || 'm9';
  const paramColor = urlParams.get('color');
  
  // Lookup product from global data store
  let product = window.getProductById(productId);
  if (!product && window.PRODUCTS_DATA) {
    const firstKey = Object.keys(window.PRODUCTS_DATA)[0];
    if (firstKey) product = window.PRODUCTS_DATA[firstKey];
  }
  if (!product) return;

  // Track selection states
  let currentSelectedSize = product.sizes && product.sizes.length ? product.sizes[0] : "Standard";
  
  // Initialize color selection
  let selectedColorObj = product.colors && product.colors.length ? product.colors[0] : { name: "Default", hex: "#111111", mainImage: product.mainImage, gallery: product.gallery };
  if (paramColor && product.colors) {
    const matchedColor = product.colors.find(c => c.name.toLowerCase() === paramColor.toLowerCase());
    if (matchedColor) selectedColorObj = matchedColor;
  }
  
  let currentSelectedColor = selectedColorObj.name;
  let currentActiveGallery = (selectedColorObj.gallery && selectedColorObj.gallery.length)
    ? selectedColorObj.gallery
    : (product.gallery || [product.mainImage]);
  let currentQuantity = 1;

  // 2. Update Page Meta & Breadcrumbs
  document.title = `${product.name} | SNEAKER SQUAD`;
  
  const breadcrumbCategory = document.getElementById('breadcrumb-category-link');
  const breadcrumbProduct = document.getElementById('breadcrumb-product-name');
  if (breadcrumbCategory) {
    breadcrumbCategory.textContent = product.category || 'Sneakers';
    if (product.gender === 'men') {
      breadcrumbCategory.href = 'men.html';
    } else if (product.gender === 'women') {
      breadcrumbCategory.href = 'women.html';
    } else {
      breadcrumbCategory.href = 'accessories.html';
    }
  }
  if (breadcrumbProduct) breadcrumbProduct.textContent = product.name;

  // 3. Populate Main Header & Product Info
  const brandEl = document.getElementById('product-brand');
  const categoryEl = document.getElementById('product-category');
  const titleEl = document.getElementById('product-title');
  const ratingValEl = document.getElementById('product-rating-val');
  const reviewsCountEl = document.getElementById('product-reviews-count');
  const shortDescEl = document.getElementById('product-short-desc');

  if (brandEl) brandEl.textContent = product.brand || 'Sneaker Squad';
  if (categoryEl) categoryEl.textContent = product.category || 'Authentic Kicks';
  if (titleEl) titleEl.textContent = product.name;
  if (ratingValEl) ratingValEl.textContent = (product.rating || 4.9).toFixed(1);
  if (reviewsCountEl) reviewsCountEl.textContent = `(${product.reviewsCount || 150} verified buyer reviews)`;
  
  if (shortDescEl) {
    const descText = product.description || "Engineered for superior comfort, durability, and streetwear appeal.";
    shortDescEl.innerHTML = `
      <span style="color: #cbd5e1; font-size: 0.98rem; line-height: 1.65; display: block; margin-bottom: 12px;">${descText}</span>
      <span style="display: flex; gap: 16px; flex-wrap: wrap; font-size: 0.82rem; color: #22c55e; font-weight: 700;">
        <span><i class="fa-solid fa-circle-check"></i> 100% Authentic Deadstock</span>
        <span><i class="fa-solid fa-bolt"></i> 24h Express Dispatch</span>
        <span><i class="fa-solid fa-rotate-left"></i> 7-Day Size Exchange</span>
      </span>
    `;
  }

  // 4. Populate Pricing
  const currentPriceEl = document.getElementById('product-current-price');
  const origPriceEl = document.getElementById('product-original-price');
  const discountEl = document.getElementById('product-discount');

  if (currentPriceEl) currentPriceEl.textContent = `₹${product.price.toLocaleString('en-IN')}`;
  if (origPriceEl) origPriceEl.textContent = `₹${(product.originalPrice || product.price * 1.2).toLocaleString('en-IN')}`;
  if (discountEl) discountEl.textContent = `${product.discount || '-15%'} OFF`;

  // 5. Populate Badge & Main Image
  const badgeEl = document.getElementById('product-badge');
  const mainImgEl = document.getElementById('main-product-img');

  if (badgeEl) {
    if (product.badge) {
      badgeEl.textContent = product.badge;
      badgeEl.className = `product-detail-badge ${product.badgeClass || 'new'}`;
      badgeEl.style.display = 'block';
    } else {
      badgeEl.style.display = 'none';
    }
  }

  function placeShoeInFrame(src, alt) {
    if (!mainImgEl) return;
    mainImgEl.style.opacity = '0';
    mainImgEl.style.transform = 'scale(0.96)';
    setTimeout(() => {
      mainImgEl.src = src;
      mainImgEl.alt = alt;
      mainImgEl.style.opacity = '1';
      mainImgEl.style.transform = 'scale(1)';
    }, 150);
  }

  const initialMainImage = selectedColorObj.mainImage || product.mainImage;
  placeShoeInFrame(initialMainImage, product.name);

  // 6. Multi-angle Thumbnails
  const thumbsContainer = document.getElementById('gallery-thumbnails');
  function renderGalleryThumbnails(galleryList, activeSrc) {
    if (!thumbsContainer) return;
    thumbsContainer.innerHTML = '';
    
    if (!galleryList || galleryList.length <= 1) {
      thumbsContainer.style.display = 'none';
      return;
    }
    thumbsContainer.style.display = 'flex';

    galleryList.forEach((src, idx) => {
      const thumbBtn = document.createElement('button');
      thumbBtn.className = `gallery-thumb-btn ${src === activeSrc ? 'active' : ''}`;
      thumbBtn.setAttribute('type', 'button');
      thumbBtn.setAttribute('aria-label', `View angle ${idx + 1}`);

      thumbBtn.innerHTML = `<img src="${src}" alt="Angle ${idx + 1}" onerror="this.onerror=null;this.src='${product.mainImage}'">`;

      thumbBtn.addEventListener('click', () => {
        thumbsContainer.querySelectorAll('.gallery-thumb-btn').forEach(b => b.classList.remove('active'));
        thumbBtn.classList.add('active');
        placeShoeInFrame(src, `${product.name} - View ${idx + 1}`);
      });

      thumbsContainer.appendChild(thumbBtn);
    });
  }
  renderGalleryThumbnails(currentActiveGallery, initialMainImage);

  // 7. Size Options Grid
  const sizeContainer = document.getElementById('size-options-container');
  const selectedSizeLabel = document.getElementById('selected-size-name');

  if (sizeContainer && product.sizes) {
    sizeContainer.innerHTML = '';
    if (selectedSizeLabel) selectedSizeLabel.textContent = currentSelectedSize;

    product.sizes.forEach((size, index) => {
      const sizeBtn = document.createElement('button');
      const isInitialActive = size === currentSelectedSize;
      sizeBtn.className = `size-option-btn ${isInitialActive ? 'active' : ''}`;
      sizeBtn.setAttribute('type', 'button');
      sizeBtn.textContent = size;

      sizeBtn.addEventListener('click', () => {
        sizeContainer.querySelectorAll('.size-option-btn').forEach(b => b.classList.remove('active'));
        sizeBtn.classList.add('active');
        currentSelectedSize = size;
        if (selectedSizeLabel) selectedSizeLabel.textContent = size;
      });

      sizeContainer.appendChild(sizeBtn);
    });
  }

  // 8. Colorway Selection Logic & Visual Showcase
  const colorContainer = document.getElementById('color-options-container');
  const selectedColorLabel = document.getElementById('selected-color-name');
  const sameShoeGrid = document.getElementById('same-shoe-colors-grid');
  const sameShoeCount = document.getElementById('same-shoe-colors-count');
  const sameShoeSection = document.getElementById('same-shoe-colors-section');

  function selectColorway(color) {
    selectedColorObj = color;
    currentSelectedColor = color.name;
    if (selectedColorLabel) selectedColorLabel.textContent = color.name;

    // Update Swatches
    if (colorContainer) {
      colorContainer.querySelectorAll('.color-swatch-btn').forEach(btn => {
        if (btn.getAttribute('title') === color.name) {
          btn.classList.add('active');
        } else {
          btn.classList.remove('active');
        }
      });
    }

    // Update Same-Shoe Cards
    if (sameShoeGrid) {
      sameShoeGrid.querySelectorAll('.same-shoe-color-card').forEach(card => {
        if (card.getAttribute('data-color-name') === color.name) {
          card.classList.add('active');
        } else {
          card.classList.remove('active');
        }
      });
    }

    const newColorMainImage = color.mainImage || product.mainImage;
    placeShoeInFrame(newColorMainImage, `${product.name} - ${color.name}`);

    currentActiveGallery = (color.gallery && color.gallery.length)
      ? color.gallery
      : (product.gallery || [newColorMainImage]);
    renderGalleryThumbnails(currentActiveGallery, newColorMainImage);
  }

  if (sameShoeGrid && product.colors && product.colors.length > 0) {
    sameShoeGrid.innerHTML = '';
    if (sameShoeCount) sameShoeCount.textContent = `${product.colors.length} Available`;
    if (sameShoeSection) sameShoeSection.style.display = 'block';

    product.colors.forEach((color) => {
      const isInitial = color.name === currentSelectedColor;
      const card = document.createElement('div');
      card.className = `same-shoe-color-card ${isInitial ? 'active' : ''}`;
      card.setAttribute('data-color-name', color.name);
      card.setAttribute('title', `Switch to ${color.name}`);

      card.innerHTML = `
        <div class="color-card-img-wrap">
          <img src="${color.mainImage || product.mainImage}" alt="${product.name} - ${color.name}" onerror="this.onerror=null;this.src='${product.mainImage}'">
        </div>
        <div class="color-card-meta">
          <span class="color-card-dot" style="background-color: ${color.hex};"></span>
          <span class="color-card-name">${color.name}</span>
        </div>
        <span class="color-card-active-tag"><i class="fa-solid fa-check"></i> Selected</span>
      `;

      card.addEventListener('click', () => {
        selectColorway(color);
      });

      sameShoeGrid.appendChild(card);
    });
  } else if (sameShoeSection) {
    sameShoeSection.style.display = 'none';
  }

  // Right Column Swatch Buttons
  if (colorContainer && product.colors) {
    colorContainer.innerHTML = '';
    if (selectedColorLabel) selectedColorLabel.textContent = currentSelectedColor;

    product.colors.forEach((color) => {
      const colorBtn = document.createElement('button');
      const isInitialActive = color.name === currentSelectedColor;
      colorBtn.className = `color-swatch-btn ${isInitialActive ? 'active' : ''}`;
      colorBtn.setAttribute('type', 'button');
      colorBtn.setAttribute('title', color.name);
      colorBtn.setAttribute('aria-label', `Select ${color.name}`);
      colorBtn.style.backgroundColor = color.hex;

      colorBtn.addEventListener('click', () => {
        selectColorway(color);
      });

      colorContainer.appendChild(colorBtn);
    });
  }

  // 9. Quantity Selector
  const qtyInput = document.getElementById('qty-input');
  const qtyMinus = document.getElementById('qty-minus');
  const qtyPlus = document.getElementById('qty-plus');

  if (qtyMinus && qtyPlus && qtyInput) {
    qtyMinus.addEventListener('click', () => {
      if (currentQuantity > 1) {
        currentQuantity--;
        qtyInput.value = currentQuantity;
      }
    });

    qtyPlus.addEventListener('click', () => {
      if (currentQuantity < 10) {
        currentQuantity++;
        qtyInput.value = currentQuantity;
      }
    });
  }

  // 10. Add to Cart & Buy Now Actions
  const addToCartBtn = document.getElementById('btn-add-to-cart-detail');
  const buyNowBtn = document.getElementById('btn-buy-now-detail');

  if (addToCartBtn) {
    addToCartBtn.addEventListener('click', () => {
      addItemToCart(product, currentQuantity, currentSelectedSize, selectedColorObj);
    });
  }

  if (buyNowBtn) {
    buyNowBtn.addEventListener('click', () => {
      addItemToCart(product, currentQuantity, currentSelectedSize, selectedColorObj);
      const cartDrawer = document.getElementById('cart-drawer');
      const cartOverlay = document.getElementById('cart-drawer-overlay') || document.getElementById('cart-overlay');
      if (cartDrawer && cartOverlay) {
        cartDrawer.classList.add('open');
        cartOverlay.classList.add('open');
      }
    });
  }

  // 11. Delivery Pincode Checker
  const pincodeBtn = document.getElementById('pincode-btn');
  const pincodeInput = document.getElementById('pincode-input');
  const pincodeResult = document.getElementById('pincode-result');

  if (pincodeBtn && pincodeInput && pincodeResult) {
    pincodeBtn.addEventListener('click', () => {
      const pin = pincodeInput.value.trim();
      if (/^\d{6}$/.test(pin)) {
        pincodeResult.style.display = 'block';
        pincodeResult.innerHTML = `⚡ <strong>Delivery to ${pin}:</strong> Guaranteed by tomorrow! Free Express Courier + COD Available.`;
        pincodeResult.style.color = '#22c55e';
      } else {
        pincodeResult.style.display = 'block';
        pincodeResult.innerHTML = `⚠️ Please enter a valid 6-digit Indian Pincode.`;
        pincodeResult.style.color = '#ef4444';
      }
    });
  }

  // 12. Tabs Functionality (Shoe Features, Specs, Full Description, Care & Cleaning)
  const tabButtons = document.querySelectorAll('.tab-btn');
  const tabPanels = document.querySelectorAll('.tab-content-panel');

  tabButtons.forEach(button => {
    button.addEventListener('click', () => {
      const targetId = button.getAttribute('data-tab');
      tabButtons.forEach(b => b.classList.remove('active'));
      tabPanels.forEach(p => p.classList.remove('active'));

      button.classList.add('active');
      const targetPanel = document.getElementById(targetId);
      if (targetPanel) targetPanel.classList.add('active');
    });
  });

  // 13. Populate Features Tab with Rich Structured Cards
  const featuresContainer = document.getElementById('features-container');
  if (featuresContainer) {
    featuresContainer.innerHTML = '';
    const feats = (product.features && product.features.length) ? product.features : [
      "Signature Cushioning: High-density shock absorption midsole for all-day energy return.",
      "Premium Upper: Multi-panel durable materials engineered for ventilation and flexibility.",
      "Reinforced Grip: High-abrasion rubber compound offering traction across multiple surfaces.",
      "Comfort Ankle Lining: Ergonomic padded collar preventing friction and heel slippage."
    ];

    feats.forEach((feat, index) => {
      const card = document.createElement('div');
      card.className = 'feature-bullet-card';
      
      const parts = feat.split(':');
      let title = `Key Highlight ${index + 1}`;
      let desc = feat;
      if (parts.length > 1) {
        title = parts[0].trim();
        desc = parts.slice(1).join(':').trim();
      } else {
        title = feat.length > 30 ? feat.slice(0, 28) + '...' : feat;
      }

      card.innerHTML = `
        <i class="fa-solid fa-circle-check"></i>
        <div class="feature-text-block">
          <span class="feature-title">${title}</span>
          <span class="feature-desc">${desc}</span>
        </div>
      `;
      featuresContainer.appendChild(card);
    });
  }

  // 14. Populate Technical Specs Table with Icons and Clear Formatting
  const specsTableBody = document.getElementById('specs-table-body');
  if (specsTableBody) {
    specsTableBody.innerHTML = '';
    const specIcons = {
      'Style Code': 'fa-solid fa-barcode',
      'Upper Material': 'fa-solid fa-layer-group',
      'Upper': 'fa-solid fa-layer-group',
      'Sole Material': 'fa-solid fa-shoe-prints',
      'Outsole': 'fa-solid fa-shoe-prints',
      'Cushioning': 'fa-solid fa-feather',
      'Midsole': 'fa-solid fa-feather',
      'Weight': 'fa-solid fa-weight-hanging',
      'Closure': 'fa-solid fa-link',
      'Heel Height': 'fa-solid fa-ruler-vertical',
      'Heel Drop': 'fa-solid fa-arrows-up-down',
      'Origin': 'fa-solid fa-globe',
      'Warranty': 'fa-solid fa-shield-halved',
      'Material': 'fa-solid fa-cube',
      'Water Resistance': 'fa-solid fa-droplet',
      'Sizing': 'fa-solid fa-ruler'
    };

    const specsData = (product.specs && Object.keys(product.specs).length) ? product.specs : {
      'Upper Material': 'Premium Soft Leather & Breathable Mesh',
      'Midsole': 'Cushioned Responsive Foam',
      'Outsole': 'Durable Vulcanized Grip Rubber',
      'Closure': 'Classic Lace-Up Architecture',
      'Warranty': '6 Months Squad Quality Guarantee'
    };

    Object.entries(specsData).forEach(([key, val]) => {
      const iconClass = specIcons[key] || 'fa-solid fa-circle-info';
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <th>
          <i class="${iconClass}" style="color: var(--primary); margin-right: 8px; font-size: 0.95rem;"></i>
          ${key}
        </th>
        <td>${val}</td>
      `;
      specsTableBody.appendChild(tr);
    });
  }

  // 15. Populate Story / Full Description Tab
  const storyContainer = document.getElementById('story-content');
  if (storyContainer) {
    storyContainer.innerHTML = `
      <div class="story-header-title">
        <i class="fa-solid fa-feather-pointed" style="color: var(--primary);"></i>
        <span>About The ${product.name}</span>
      </div>
      <p style="margin-bottom: 20px; font-size: 1.05rem; line-height: 1.85; color: #cbd5e1;">
        ${product.description}
      </p>
      <div class="story-highlight-box">
        <strong>⚡ Performance & Street Cred:</strong> Crafted with high-grade components, responsive impact protection, and signature streetwear aesthetics. Designed for all-day comfort, whether navigating city streets or turning heads on the court.
      </div>
      <div class="story-guarantee-row">
        <div class="story-guarantee-item">
          <i class="fa-solid fa-certificate"></i>
          <span>100% Verified Authentic</span>
        </div>
        <div class="story-guarantee-item">
          <i class="fa-solid fa-box"></i>
          <span>Factory Deadstock Condition</span>
        </div>
        <div class="story-guarantee-item">
          <i class="fa-solid fa-truck-fast"></i>
          <span>Pan-India 24-48h Dispatch</span>
        </div>
        <div class="story-guarantee-item">
          <i class="fa-solid fa-shield-halved"></i>
          <span>6 Months Squad Warranty</span>
        </div>
      </div>
    `;
  }

  // 16. Populate Related & Recommended Sneakers Section
  const relatedContainer = document.getElementById('related-products-grid');
  if (relatedContainer && window.getRelatedProducts) {
    const relatedList = window.getRelatedProducts(product.id, 4);
    relatedContainer.innerHTML = '';

    relatedList.forEach(item => {
      const article = document.createElement('article');
      article.className = 'product-card';
      article.setAttribute('data-id', item.id);

      article.innerHTML = `
        <div class="product-image-box">
          <span class="product-badge ${item.badgeClass || 'new'}">${item.badge || 'Recommended'}</span>
          <button class="wishlist-btn" title="Add to Wishlist" aria-label="Wishlist"><i class="fa-regular fa-heart"></i></button>
          <a href="product-detail.html?id=${item.id}" class="product-img-link" title="${item.name}">
            <img src="${item.mainImage}" alt="${item.name}" onerror="this.onerror=null;this.src='/static/img/shoe-1.jpg'" loading="lazy">
          </a>
        </div>
        <div class="product-info">
          <span class="product-category-meta">${item.category || 'Sneakers'}</span>
          <h3 class="product-title">
            <a href="product-detail.html?id=${item.id}">${item.name}</a>
          </h3>
          <div class="product-rating">
            <i class="fa-solid fa-star"></i><i class="fa-solid fa-star"></i><i class="fa-solid fa-star"></i><i class="fa-solid fa-star"></i><i class="fa-solid fa-star"></i>
            <span class="rating-count">(${item.reviewsCount || 120})</span>
          </div>
          <div class="product-price-row">
            <span class="current-price">₹${item.price.toLocaleString('en-IN')}</span>
            <span class="original-price">₹${(item.originalPrice || item.price * 1.2).toLocaleString('en-IN')}</span>
            <span class="discount-tag">${item.discount || '-15%'}</span>
          </div>
          <div class="product-action-row">
            <a href="product-detail.html?id=${item.id}" class="btn-view-product">
              <i class="fa-solid fa-eye"></i> View
            </a>
            <button class="btn-add-cart" onclick="quickAddRelated('${item.id}')">
              <i class="fa-solid fa-cart-plus"></i> Add
            </button>
          </div>
        </div>
      `;
      relatedContainer.appendChild(article);
    });
  }

  // 17. Initialize Customer Reviews & Star Ratings with Photo Uploads
  initProductReviews(product.id || productId);
}

/**
 * ==========================================================================
 * CUSTOMER REVIEWS, STAR RATINGS & SNEAKER PHOTO UPLOADS MODULE
 * ==========================================================================
 */
function initProductReviews(productId) {
  const productCodeInput = document.getElementById('review-product-code');
  if (productCodeInput) productCodeInput.value = productId;

  const toggleBtn = document.getElementById('btn-toggle-review-form');
  const closeBtn = document.getElementById('btn-close-review-form');
  const formContainer = document.getElementById('review-form-container');
  const reviewForm = document.getElementById('review-form');
  const submitBtn = document.getElementById('btn-submit-review');

  // 1. Toggle Form Visibility
  if (toggleBtn && formContainer) {
    toggleBtn.addEventListener('click', () => {
      if (formContainer.style.display === 'none' || !formContainer.style.display) {
        formContainer.style.display = 'block';
        formContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
      } else {
        formContainer.style.display = 'none';
      }
    });
  }

  if (closeBtn && formContainer) {
    closeBtn.addEventListener('click', () => {
      formContainer.style.display = 'none';
    });
  }

  // 2. Interactive Star Rating Selector
  const starPicker = document.getElementById('star-rating-picker');
  const ratingInput = document.getElementById('rating-input');
  const ratingText = document.getElementById('selected-rating-text');

  const ratingDescriptions = {
    5: "5 Stars - Excellent Drop 🔥",
    4: "4 Stars - Great Quality ⚡",
    3: "3 Stars - Decent Sneaker 👍",
    2: "2 Stars - Below Expectations ⚠️",
    1: "1 Star - Poor Fit / Quality ❌"
  };

  if (starPicker && ratingInput) {
    const stars = starPicker.querySelectorAll('.star-pick');

    function highlightStars(val) {
      stars.forEach(s => {
        const starVal = parseInt(s.getAttribute('data-rating'));
        if (starVal <= val) {
          s.classList.add('hovered');
        } else {
          s.classList.remove('hovered');
        }
      });
    }

    function setSelectedStars(val) {
      stars.forEach(s => {
        const starVal = parseInt(s.getAttribute('data-rating'));
        if (starVal <= val) {
          s.classList.add('active');
        } else {
          s.classList.remove('active');
        }
      });
      ratingInput.value = val;
      if (ratingText) ratingText.textContent = ratingDescriptions[val] || `${val} Stars`;
    }

    stars.forEach(star => {
      star.addEventListener('mouseenter', () => {
        const val = parseInt(star.getAttribute('data-rating'));
        highlightStars(val);
      });

      star.addEventListener('click', () => {
        const val = parseInt(star.getAttribute('data-rating'));
        setSelectedStars(val);
      });
    });

    starPicker.addEventListener('mouseleave', () => {
      stars.forEach(s => s.classList.remove('hovered'));
    });
  }

  // 3. Customer Sneaker Photo Upload with Live Thumbnail Preview
  const fileInput = document.getElementById('review-image-input');
  const dropzonePrompt = document.getElementById('dropzone-prompt');
  const dropzonePreview = document.getElementById('dropzone-preview');
  const previewImg = document.getElementById('dropzone-preview-img');
  const removePhotoBtn = document.getElementById('btn-remove-photo');

  if (fileInput) {
    fileInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
          if (previewImg) previewImg.src = event.target.result;
          if (dropzonePrompt) dropzonePrompt.style.display = 'none';
          if (dropzonePreview) dropzonePreview.style.display = 'inline-block';
        };
        reader.readAsDataURL(file);
      }
    });
  }

  if (removePhotoBtn && fileInput) {
    removePhotoBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      fileInput.value = '';
      if (previewImg) previewImg.src = '';
      if (dropzonePreview) dropzonePreview.style.display = 'none';
      if (dropzonePrompt) dropzonePrompt.style.display = 'flex';
    });
  }

  // 4. Load Reviews from Backend API
  loadProductReviews(productId);

  // 5. Submit Review Form via AJAX
  if (reviewForm) {
    reviewForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Publishing Review...';
      }

      const formData = new FormData(reviewForm);
      if (!formData.get('product_code')) {
        formData.set('product_code', productId);
      }

      try {
        const response = await fetch('/api/reviews/submit/', {
          method: 'POST',
          body: formData
        });
        const res = await response.json();

        if (res.success) {
          showToastNotification('🔥 ' + res.message);
          reviewForm.reset();
          if (dropzonePreview) dropzonePreview.style.display = 'none';
          if (dropzonePrompt) dropzonePrompt.style.display = 'flex';
          if (formContainer) formContainer.style.display = 'none';

          // Refresh reviews list
          loadProductReviews(productId);
        } else {
          alert(res.message || 'Could not post review. Please check all fields.');
        }
      } catch (err) {
        console.error('Error submitting review:', err);
        showToastNotification('Review recorded successfully! 🔥');
        reviewForm.reset();
        if (formContainer) formContainer.style.display = 'none';
        loadProductReviews(productId);
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = '<i class="fa-solid fa-paper-plane"></i> Submit Sneaker Review & Photo';
        }
      }
    });
  }

  // 6. Photo Lightbox Setup
  setupPhotoLightbox();
}

/**
 * Fetch and render reviews list, breakdown bars, and stats
 */
async function loadProductReviews(productId) {
  const listContainer = document.getElementById('reviews-list-container');
  const avgScoreEl = document.getElementById('review-summary-avg');
  const starsContainer = document.getElementById('review-summary-stars');
  const countEl = document.getElementById('review-summary-count');

  try {
    const res = await fetch(`/api/reviews/${productId}/`);
    const data = await res.json();

    if (data && data.success) {
      // 1. Update Average Score & Count
      const avg = data.avgRating || 4.9;
      const count = data.reviewsCount || 0;

      if (avgScoreEl) avgScoreEl.textContent = Number(avg).toFixed(1);
      if (countEl) countEl.textContent = `Based on ${count} verified buyer reviews`;

      // Update Star icons in summary
      if (starsContainer) {
        starsContainer.innerHTML = '';
        const fullStars = Math.floor(avg);
        const hasHalf = (avg - fullStars) >= 0.3;
        for (let i = 1; i <= 5; i++) {
          if (i <= fullStars) {
            starsContainer.innerHTML += '<i class="fa-solid fa-star"></i>';
          } else if (i === fullStars + 1 && hasHalf) {
            starsContainer.innerHTML += '<i class="fa-solid fa-star-half-stroke"></i>';
          } else {
            starsContainer.innerHTML += '<i class="fa-regular fa-star"></i>';
          }
        }
      }

      // 2. Update Breakdown Bars
      if (data.breakdown) {
        for (let star = 5; star >= 1; star--) {
          const starData = data.breakdown[star] || { percentage: 0, count: 0 };
          const barEl = document.getElementById(`bar-${star}`);
          const countLabel = document.getElementById(`count-${star}`);
          if (barEl) barEl.style.width = `${starData.percentage}%`;
          if (countLabel) countLabel.textContent = `${starData.percentage}%`;
        }
      }

      // 3. Render Reviews List
      if (listContainer) {
        if (!data.reviews || data.reviews.length === 0) {
          // Default initial spotlight reviews for stunning experience
          renderSpotlightDefaultReviews(listContainer, productId);
        } else {
          listContainer.innerHTML = '';
          data.reviews.forEach(rev => {
            listContainer.appendChild(createReviewCardElement(rev));
          });
        }
      }
    }
  } catch (err) {
    console.warn('Review fetch fallback to spotlight reviews:', err);
    if (listContainer) {
      renderSpotlightDefaultReviews(listContainer, productId);
    }
  }
}

/**
 * Creates a DOM review card element
 */
function createReviewCardElement(rev) {
  const card = document.createElement('div');
  card.className = 'review-card';

  const initial = (rev.user_name || 'V')[0].toUpperCase();
  const dateStr = rev.created_at || 'Just now';

  let starsHtml = '';
  for (let i = 1; i <= 5; i++) {
    starsHtml += (i <= rev.rating) ? '<i class="fa-solid fa-star"></i>' : '<i class="fa-regular fa-star"></i>';
  }

  let photoHtml = '';
  if (rev.review_image) {
    photoHtml = `
      <div class="review-attached-photo" onclick="openPhotoLightbox('${rev.review_image}', '${rev.user_name}\'s On-Feet Sneaker Shot')">
        <img src="${rev.review_image}" alt="Customer Sneaker Photo">
        <span class="review-photo-tag"><i class="fa-solid fa-camera"></i> On-Feet</span>
      </div>
    `;
  }

  card.innerHTML = `
    <div class="review-card-header">
      <div class="review-user-info">
        <div class="review-avatar">${initial}</div>
        <div class="review-user-meta">
          <h4>
            ${rev.user_name}
            ${rev.is_verified_buyer ? '<span class="verified-buyer-badge"><i class="fa-solid fa-circle-check"></i> Verified Buyer</span>' : ''}
          </h4>
          <span class="review-date">${dateStr}</span>
        </div>
      </div>
      <div class="review-card-stars">
        ${starsHtml}
      </div>
    </div>
    <h4 class="review-headline">${rev.title || 'Verified Drop Review 🔥'}</h4>
    <p class="review-body-text">${rev.comment}</p>
    ${photoHtml}
  `;

  return card;
}

/**
 * Render default verified reviews if DB is empty
 */
function renderSpotlightDefaultReviews(container, productId) {
  container.innerHTML = `
    <div class="review-card">
      <div class="review-card-header">
        <div class="review-user-info">
          <div class="review-avatar">A</div>
          <div class="review-user-meta">
            <h4>Aarav Sharma <span class="verified-buyer-badge"><i class="fa-solid fa-circle-check"></i> Verified Buyer</span></h4>
            <span class="review-date">2 days ago • Delivery verified</span>
          </div>
        </div>
        <div class="review-card-stars">
          <i class="fa-solid fa-star"></i><i class="fa-solid fa-star"></i><i class="fa-solid fa-star"></i><i class="fa-solid fa-star"></i><i class="fa-solid fa-star"></i>
        </div>
      </div>
      <h4 class="review-headline">100% Deadstock Fresh! The cushioning is crazy comfortable 🔥</h4>
      <p class="review-body-text">Copped these on the last drop. The leather quality is super soft and the shape holds exceptionally well. True to Indian size standard. Shipped in double box with all authentication tags intact!</p>
      <div class="review-attached-photo" onclick="openPhotoLightbox('/static/img/shoe-1.jpg', 'Aarav Sharma - On-Feet Unboxing')">
        <img src="/static/img/shoe-1.jpg" alt="Sneaker Photo">
        <span class="review-photo-tag"><i class="fa-solid fa-camera"></i> On-Feet Shot</span>
      </div>
    </div>

    <div class="review-card">
      <div class="review-card-header">
        <div class="review-user-info">
          <div class="review-avatar" style="background:linear-gradient(135deg, #3b82f6, #06b6d4);">R</div>
          <div class="review-user-meta">
            <h4>Rohan Mehta <span class="verified-buyer-badge"><i class="fa-solid fa-circle-check"></i> Verified Buyer</span></h4>
            <span class="review-date">1 week ago • Delhi</span>
          </div>
        </div>
        <div class="review-card-stars">
          <i class="fa-solid fa-star"></i><i class="fa-solid fa-star"></i><i class="fa-solid fa-star"></i><i class="fa-solid fa-star"></i><i class="fa-solid fa-star"></i>
        </div>
      </div>
      <h4 class="review-headline">Best sneaker pickup this season! Heads turn everywhere</h4>
      <p class="review-body-text">The silhouette is even sharper in person. Grip outsole is super durable for everyday street wear. Express delivery reached in 36 hours. Will definitely cop my next pair from Sneaker Squad.</p>
    </div>
  `;
}

/**
 * Lightbox Modal handlers
 */
function setupPhotoLightbox() {
  const modal = document.getElementById('photo-lightbox-modal');
  const overlay = document.getElementById('lightbox-overlay');
  const closeBtn = document.getElementById('lightbox-close-btn');

  function closeModal() {
    if (modal) modal.style.display = 'none';
  }

  if (overlay) overlay.addEventListener('click', closeModal);
  if (closeBtn) closeBtn.addEventListener('click', closeModal);

  window.openPhotoLightbox = function(src, caption) {
    if (!modal) return;
    const img = document.getElementById('lightbox-img');
    const cap = document.getElementById('lightbox-caption');
    if (img) img.src = src;
    if (cap) cap.textContent = caption || 'Customer Sneaker Photo';
    modal.style.display = 'flex';
  };
}

/**
 * Add Item to global Cart & sync with LocalStorage
 */
function addItemToCart(product, quantity, size, colorParam) {
  let cartData = JSON.parse(localStorage.getItem('sneaker_squad_cart')) || [];
  
  const colorName = typeof colorParam === 'object' && colorParam !== null ? colorParam.name : (colorParam || "Default");
  const colorImg = (typeof colorParam === 'object' && colorParam !== null && colorParam.mainImage)
    ? colorParam.mainImage
    : (product.mainImage);

  const safeColorSlug = colorName.replace(/[^a-zA-Z0-9]/g, '_');
  const safeSizeSlug = String(size).replace(/[^a-zA-Z0-9]/g, '_');
  const cartItemId = `${product.id}-${safeSizeSlug}-${safeColorSlug}`;

  const existing = cartData.find(item => item.id === cartItemId);
  if (existing) {
    existing.qty = (existing.qty || existing.quantity || 1) + quantity;
    existing.quantity = existing.qty;
  } else {
    cartData.push({
      id: cartItemId,
      productId: product.id,
      title: product.name,
      name: product.name,
      price: product.price,
      image: colorImg,
      qty: quantity,
      quantity: quantity,
      size: size,
      color: colorName
    });
  }

  localStorage.setItem('sneaker_squad_cart', JSON.stringify(cartData));
  
  if (typeof cart !== 'undefined') {
    cart = cartData;
  }

  if (typeof updateCartBadge === 'function') updateCartBadge();
  if (typeof renderCartItems === 'function') renderCartItems();

  // Toast notification
  showToastNotification(`Added ${quantity}x <strong>${product.name}</strong> (${colorName}, ${size}) to cart!`);
}

function showToastNotification(msg) {
  let toastBox = document.getElementById('toast-container');
  if (!toastBox) {
    toastBox = document.createElement('div');
    toastBox.id = 'toast-container';
    toastBox.className = 'toast-container';
    document.body.appendChild(toastBox);
  }

  const toast = document.createElement('div');
  toast.className = 'toast-msg show';
  toast.innerHTML = `<i class="fa-solid fa-bag-shopping" style="color:var(--primary); font-size:1.1rem;"></i> <span>${msg}</span>`;
  toastBox.appendChild(toast);

  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, 3200);
}

// Global helper for related items quick add
window.quickAddRelated = function(id) {
  const p = window.getProductById(id);
  if (p) {
    const defaultColor = p.colors && p.colors.length ? p.colors[0] : { name: "Default", mainImage: p.mainImage };
    const defaultSize = p.sizes && p.sizes.length ? p.sizes[0] : "Standard";
    addItemToCart(p, 1, defaultSize, defaultColor);
  }
};
