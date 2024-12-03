const allSideMenu = document.querySelectorAll("#sidebar .side-menu.top li a");

allSideMenu.forEach((item) => {
  const li = item.parentElement;

  item.addEventListener("click", function () {
    // if(document.querySelector('.active .sub-menu-container') !== null)
    // 	document.querySelector('.active .sub-menu-container').setAttribute('style', 'display: none');
    allSideMenu.forEach((i) => {
      i.parentElement.classList.remove("active");
    });
    li.classList.add("active");
    // document.querySelector('.active .sub-menu-container').setAttribute('style', 'display: block');
  });
});

// TOGGLE SIDEBAR
const menuBar = document.querySelector("#content nav .bx.bx-menu");
const sidebar = document.getElementById("sidebar");

menuBar.addEventListener("click", function () {
  sidebar.classList.toggle("hide");
});

const searchButton = document.querySelector(
  "#content nav form .form-input button"
);
const searchButtonIcon = document.querySelector(
  "#content nav form .form-input button .bx"
);
const searchForm = document.querySelector("#content nav form");

searchButton.addEventListener("click", function (e) {
  if (window.innerWidth < 576) {
    e.preventDefault();
    searchForm.classList.toggle("show");
    if (searchForm.classList.contains("show")) {
      searchButtonIcon.classList.replace("bx-search", "bx-x");
    } else {
      searchButtonIcon.classList.replace("bx-x", "bx-search");
    }
  }
});

if (window.innerWidth < 768) {
  sidebar.classList.add("hide");
} else if (window.innerWidth > 576) {
  searchButtonIcon.classList.replace("bx-x", "bx-search");
  searchForm.classList.remove("show");
}

window.addEventListener("resize", function () {
  if (this.innerWidth > 576) {
    searchButtonIcon.classList.replace("bx-x", "bx-search");
    searchForm.classList.remove("show");
  }
});

const switchMode = document.getElementById("switch-mode");

switchMode.addEventListener("change", function () {
  if (this.checked) {
    document.body.classList.add("dark");
  } else {
    document.body.classList.remove("dark");
  }
});

// popup

function confirmLockAccount(event, accountId) {
  // Nội dung của hàm confirmLockAccount
  event.preventDefault(); // Ngăn chặn hành động mặc định của liên kết
  Swal.fire({
    title: "Bạn có chắc chắn?",
    text: "Bạn có chắc chắn muốn khóa tài khoản này không?",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Có, khóa ngay!",
    cancelButtonText: "Hủy",
  }).then((result) => {
    if (result.isConfirmed) {
      // Thực hiện hành động khóa tài khoản
      window.location.href = `/admin/account/lock/${accountId}`; // Thay đổi đường dẫn này thành đường dẫn thực tế
    }
  });
}

function confirmLockUser(event, userId) {
  // Nội dung của hàm confirmLockUser
  event.preventDefault(); // Ngăn chặn hành động mặc định của liên kết
  Swal.fire({
    title: "Bạn có chắc chắn?",
    text: "Bạn có chắc chắn muốn khóa người dùng này không?",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Có, khóa ngay!",
    cancelButtonText: "Hủy",
  }).then((result) => {
    if (result.isConfirmed) {
      // Thực hiện hành động khóa người dùng
      window.location.href = "/admin/user/lock/" + userId; // Thay đổi đường dẫn này thành đường dẫn thực tế
    }
  });
}
