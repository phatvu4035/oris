odoo.define('theme_oristar.ProductList', function(require) {
    "use strict";
    $(document).ready(function () {
        var href = window.location.href;
        const url = new URL(href);
        var origin_location = window.origin;
        const searchParams = new URLSearchParams(url.search);

        if(searchParams.get('product_name') && searchParams.get('product_name') == 'asc') {
            $('#shop_order').val('product_name_asc')
        } else if(searchParams.get('product_name') && searchParams.get('product_name') == 'desc') {
            $('#shop_order').val('product_name_desc')
        }
        $('#shop_order').change(function (ev) {
            var $target = $(ev.target);
            var val = $target.val();
            if(val == 'product_name_asc') {
                searchParams.set('product_name', 'asc');
            } else if(val == 'product_name_desc') {
                searchParams.set('product_name', 'desc');
            }
            window.location.href = origin_location + '/shop' + '?' + searchParams.toString();
        });
        $("#col-6").click(function () {
            $(".sumale").removeClass("col-lg-4").addClass("col-lg-6");
        });
        $("#col-4").click(function () {
            $(".sumale").removeClass("col-lg-6").addClass("col-lg-4");
        });
        var swiper = new Swiper(".mySwiper", {
            slidesPerView: 2,
            spaceBetween: 30,
            cssMode: true,
            navigation: {
                nextEl: ".swiper-button-next",
                prevEl: ".swiper-button-prev",
            },
            pagination: {
                el: ".swiper-pagination",
            },
            mousewheel: true,
            keyboard: true,
            breakpoints: {
                0: {
                    slidesPerView: 1,
                    spaceBetween: 12,
                },
                640: {
                    slidesPerView: 2,
                    spaceBetween: 12,
                },
                768: {
                    slidesPerView: 3,
                    spaceBetween: 15,
                },
                1024: {
                    slidesPerView: 4,
                },
            },
        });
        limit_character_title(56);
    });
    function limit_character_title(max) {
        setTimeout(function()
        {
            var tot, str;
            $('.category-product .text h3 a').each(function() {
                str = String($(this).html());
                tot = str.length;
                str = (tot <= max)
                    ? str
                  : str.substring(0,(max + 1))+"...";
                $(this).html(str);
           });
        },200); // Delayed for example only.
    }
});