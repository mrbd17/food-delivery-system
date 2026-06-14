import { toggleCart, initCartUI} from "../cart/cartUI.js";

import { AuthAPI } from "../auth/auth.service.js";
const authAPI = new AuthAPI();

const logoutBtn = document.getElementById("logout-btn");
if(logoutBtn){
  logoutBtn.addEventListener("click", handleLogout);
  console.log("logout exists")
}


async function handleLogout(e) {
    e.preventDefault();

    const result = await authAPI.logout();

    if (result.success) {
      setTimeout(() => {
        window.location.href = "/";
      }, 3000)
        
    } else {
        console.error(result);
        console.error("logout failed");
    }
}
const cartBtn = document.querySelector(".cart-btn");
if(cartBtn){
cartBtn.addEventListener("click", toggleCart)
}

initCartUI();
const overlay = document.querySelector('.overlay');
const navItems = document.querySelectorAll('.nav-item');



let activeMenu = null;

function closeAll() {
  document.querySelectorAll('.mega-menu').forEach(menu => menu.classList.remove('active'));
  overlay.classList.remove('active');
  activeMenu = null;
}

// Desktop hover & Mobile click
navItems.forEach(item => {
  const menuId = item.dataset.menu;
  const megaMenu = document.getElementById(menuId);

  // Desktop hover
  item.addEventListener('mouseenter', () => {
    if(window.innerWidth > 768) {
      closeAll();
      megaMenu.classList.add('active');
      overlay.classList.add('active');
      activeMenu = megaMenu;
    }
  });

  megaMenu.addEventListener('mouseenter', () => {
    if(window.innerWidth > 768) {
      megaMenu.classList.add('active');
      overlay.classList.add('active');
      activeMenu = megaMenu;
    }
  });

  // Desktop leave
  item.addEventListener('mouseleave', () => {
    if(window.innerWidth > 768) {
      setTimeout(() => {
        if (!megaMenu.matches(':hover')) closeAll();
      }, 300);
    }
  });

  megaMenu.addEventListener('mouseleave', () => {
    if(window.innerWidth > 768) closeAll();
  });

  // Mobile tap
  item.addEventListener('click', (e) => {
    if(window.innerWidth <= 768){
      e.preventDefault();
      const isActive = megaMenu.classList.contains('active');
      closeAll();
      if(!isActive){
        megaMenu.classList.add('active');
        overlay.classList.add('active');
        activeMenu = megaMenu;
      }
    }
  });
});

// إغلاق عند الضغط على overlay
overlay.addEventListener('click', closeAll);

const profileBtn = document.getElementById("profileBtn");
const profileDropdown = document.getElementById("profileDropdown");
if (profileBtn){
  profileBtn.addEventListener("click", (e) => {
    e.stopPropagation(); // يمنع الغلق الفوري
    profileDropdown.classList.toggle("show");
});
}

document.addEventListener("click" , () => {
  profileDropdown.classList.remove("show");
});

if(profileDropdown){
  profileDropdown.addEventListener("click", (e) => {
    e.stopPropagation();
  }) 
}
