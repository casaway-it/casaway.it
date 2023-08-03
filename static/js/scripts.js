// =============================sticky header Start Script====================
document.addEventListener("DOMContentLoaded", function () {
    window.addEventListener('scroll', function () {
        if (window.scrollY > 83) {
            document.getElementById('navbar_top').classList.add('fixed-top');
        } else {
            document.getElementById('navbar_top').classList.remove('fixed-top');
        }
    });
});
// =============================sticky header End Script====================

// ============================navigetion menu============================= //
(function ($) {
    $.fn.menumaker = function (options) {
        var cssmenu = $(this),
            settings = $.extend({
                format: "dropdown",
                sticky: false
            }, options);
        return this.each(function () {
            $(this).find(".button").on('click', function () {
                $(this).toggleClass('menu-opened');
                var mainmenu = $(this).next('ul');
                if (mainmenu.hasClass('open')) {
                    mainmenu.slideToggle().removeClass('open');
                } else {
                    mainmenu.slideToggle().addClass('open');
                    if (settings.format === "dropdown") {
                        mainmenu.find('ul').show();
                    }
                }
            });

            cssmenu.find('li ul').parent().addClass('has-sub');
            multiTg = function () {
                cssmenu.find(".has-sub").prepend('<span class="submenu-button"></span>');
                cssmenu.find('.submenu-button').on('click', function () {
                    $(this).toggleClass('submenu-opened');
                    if ($(this).siblings('ul').hasClass('open')) {
                        $(this).siblings('ul').removeClass('open').slideToggle();
                    } else {
                        $(this).siblings('ul').addClass('open').slideToggle();
                    }
                });
            };

            if (settings.format === 'multitoggle') multiTg();
            else cssmenu.addClass('dropdown');
            if (settings.sticky === true) cssmenu.css('position', 'fixed');
            resizeFix = function () {
                var mediasize = 991;
                if ($(window).width() > mediasize) {
                    cssmenu.find(' ul').show();
                }
                if ($(window).width() <= mediasize) {
                    cssmenu.find(' ul').hide().removeClass('open');
                }
            };
            resizeFix();
            return $(window).on('resize', resizeFix);
        });
    };
})(jQuery);

(function ($) {
    $(document).ready(function () {
        $(".thmv-top-navbar").menumaker({
            format: "multitoggle"
        });
    });
})(jQuery);

document.addEventListener("DOMContentLoaded", function () {
    // make it as accordion for smaller screens
    if (window.innerWidth > 991) {
        document.querySelectorAll('.navbar .nav-item').forEach(function (everyitem) {
            everyitem.addEventListener('mouseover', function (e) {
                let el_link = this.querySelector('a[data-bs-toggle]');
                if (el_link != null) {
                    let nextEl = el_link.nextElementSibling;
                    el_link.classList.add('show');
                    nextEl.classList.add('show');
                }
            });
            everyitem.addEventListener('mouseleave', function (e) {
                let el_link = this.querySelector('a[data-bs-toggle]');
                if (el_link != null) {
                    let nextEl = el_link.nextElementSibling;
                    el_link.classList.remove('show');
                    nextEl.classList.remove('show');
                }
            })
        });
    }
});

// ====== Right side floting buttons ====== //
$(window).scroll(function () {
    var scroll = $(window).scrollTop();
    if (scroll >= 1000) {
        $(".thmv-home-side").addClass("thmv-home-side-show");
    } else {
        $(".thmv-home-side").removeClass("thmv-home-side-show");
    }
});

// home page v2 and home page v4 booking section
$(".thmv-home-v2 .thmv-booking-sec .thmv-booking-selection ul li, .thmv-choose-option .thmv-choose-room li").click(function () {
    $(".thmv-home-v2 .thmv-booking-sec .thmv-booking-selection ul li, .thmv-choose-option .thmv-choose-room li").removeClass("active");
    $(this).addClass("active");
});

// slick-image-center slider //
$(".slick-testimonial-slider").slick({
    infinite: true,
    slidesToShow: 1,
    slidesToScroll: 1,
    dots: true,
    arrows: false,
    pauseOnHover: true,
    autoplay: true,
    speed: 1000,
    autoplaySpeed: 5000,
    responsive: [{
        breakpoint: 995,
        settings: {
            centerMode: false,
            dots: true,
            slidesToShow: 1,
            slidesToScroll: 1
        }

    }]
});

// about page img slider
$('.thmv-ab-img-slider').slick({
    infinite: true,
    centerMode: true,
    slidesToShow: 2,
    slidesToScroll: 1,
    dots: false,
    arrows: false,
    pauseOnHover: true,
    autoplay: true,
    speed: 1000,
    autoplaySpeed: 3000,
    responsive: [{
        breakpoint: 992,
        settings: {
            centerMode: true,
            dots: false,
            slidesToShow: 1,
            slidesToScroll: 1
        },
        breakpoint: 767,
        settings: {
            centerMode: true,
            dots: true,
            slidesToShow: 1,
            slidesToScroll: 1
        }
    }]
});

// 
$('.slick-review-slider').slick({
    infinite: true,
    centerMode: true,
    slidesToShow: 1,
    slidesToScroll: 1,
    dots: false,
    arrows: true,
    pauseOnHover: true,
    autoplay: true,
    speed: 1000,
    autoplaySpeed: 3000,
    responsive: [{
        breakpoint: 767,
        settings: {
            centerMode: false,
            dots: false,
            slidesToShow: 1,
            slidesToScroll: 1
        }
    }]
});

// ======= home page v4 gallery filter ========//
$(".responsive-tabs > li button").click(function () {
    $(".responsive-tabs > li").removeClass("active");
    $(this).parent().addClass("active");
    $(".responsive-tabs").toggleClass("open");
});
// =======  gallery
$(document).ready(function () {

    $(".thmv-filter-button").click(function () {
        var value = $(this).attr('data-filter');

        if (value == "all") {
            $('.filter').show('1000');
        }
        else {
            $(".filter").not('.' + value).hide('3000');
            $('.filter').filter('.' + value).show('3000');
        }
    });

    $(".thmv-appartments-sec .thmv-filter-tabs  .btn-default").click(function () {
        $(".thmv-appartments-sec .thmv-filter-tabs  .btn-default").removeClass("active");
        $(this).addClass("active");
    });
});

// gallery fancybox js
Fancybox.bind('[data-fancybox="gallery"]', {
    dragToClose: false,

    Toolbar: false,
    closeButton: "top",

    Image: {
        zoom: false,
    },

});