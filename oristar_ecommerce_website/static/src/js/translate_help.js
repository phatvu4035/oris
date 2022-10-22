odoo.define('oristar_ecommerce_website.translate_help', function (require) {
    "use strict";

    var session = require('web.session');

    var terms = {
        'vi_VN': {
            'Basic shape': {
                0: 'Hình dạng cơ bản',
                1: 'Hình dạng'
            },
            'Update delivery address': 'Cập nhật địa chỉ giao hàng',
            'Update invoice address': 'Cập nhật địa chỉ xuất hóa đơn',
            'Remove product': 'Xóa sản phẩm',
            'Full Name': 'Họ và tên',
            'Country': 'Quốc gia',
            'State': 'Tỉnh/Thành phố',
            'City': 'Thành phố',
            'District': 'Quận huyện',
            'Township': 'Xã phường',
            'Detailed Address': 'Địa chỉ chi tiết',
            'ZIP / Postal Code': 'Mã bưu chính',
            'Company name (Optional)': 'Tên công ty (Tùy chọn)',
            'Company Name': 'Tên công ty',
            'VAT Number': 'Mã số thuế',
            'TAX Number': 'Mã số thuế',
            'Update': 'Cập nhật',
            'Close': 'Đóng',
            'Please enter correct email format': 'Vui lòng nhập đúng định dạng',
            'Ex': 'VD',
            'Select basic shape': 'Hình dạng cơ bản',
            'Grades': 'Hợp kim',
            'Select grades': 'Hợp kim',
            'Detailed shape': 'Hình dạng chi tiết',
            'Select detailed shape': 'Hình dạng chi tiết',
            'Material': 'Vật liệu',
            'Select material': 'Vật liệu',
            'Material category': 'Nhóm vật liệu',
            'Select material category': 'Nhóm vật liệu',
            'Origin': 'Xuất xứ',
            'Select origin': 'Xuất xứ',
            'Temper': 'Độ cứng',
            'Select temper': 'Chọn độ cứng',
            'Search': 'Tìm kiếm',
            'Order Code': 'Mã đơn hàng',
            'Order code': 'Mã đơn hàng',
            'Cancel Order': 'Hủy đơn hàng',
            'Receiver': 'Người nhận hàng',
            'Phone': 'Số điện thoại',
            'Invoice Email': 'Email xuất hóa đơn',
            'Address': 'Địa chỉ',
            'Notes': 'Ghi chú',
            'Product': 'Sản phẩm',
            'Quantity': 'Số lượng',
            'Weight (kg)': 'Khối lượng (kg)',
            'Unit price / kg': 'Đơn giá / kg',
            '(Shipping is not included)': 'Chưa bao gồm vận chuyển',
            '(Shipping included)': 'Đã bao gồm vận chuyển',
            'Total': 'Thành tiền',
            'Order date': 'Ngày đặt hàng',
            'Estimated delivery time': 'Ngày giao hàng dự kiến',
            'Amount untaxed': 'Tổng giá trị',
            'Amount total': 'Tổng hóa đơn',
            'Enter product name': 'Nhập tên sản phẩm',
            'Shipping Address': 'Địa chỉ giao hàng',
            'Invoice Address': 'Địa chỉ xuất hóa đơn',
            'Customer Name': 'Tên khách hàng',

            'tku_for_pay': 'Cảm ơn bạn đã đặt hàng Oristar. Để thanh toán đơn hàng theo hình thức Trả toàn bộ, quý khách vui lòng chuyển khoản',
            'tku_for_advan': 'Cảm ơn bạn đã đặt hàng Oristar. Để thanh toán đơn hàng theo hình thức Trả trước, quý khách vui lòng chuyển khoản',
            'acc_syntax': 'theo cú pháp sau',
            '70_per_order': '70% giá trị đơn hàng',
            'cp_ck': 'TT [dấu cách] ORISTAR [ SĐT ]',
            'acc_inf': 'THÔNG TIN TÀI KHOẢN',
            'bank_name': 'Tên ngân hàng',
            'bank_num': 'Số tài khoản',
            'Branch': 'Chi nhánh',
            'acc_own': 'Chủ tài khoản',
            'Order': 'Đặt hàng',
            'Order confirmation': 'Thông tin đơn hàng',
            'submit_success_msg': 'Đơn hàng của bạn đã được gửi yêu cầu thành công, ORISTAR sẽ đối soát lại các thông tin về đơn hàng và thông báo đến bạn trong vòng 24 tiếng qua email và số điện thoại',
            'tku_or_service': 'Cảm ơn quý khách đã sử dụng dịch vụ của ORISTAR',
            'back_to_hp': 'Quay lại trang chủ',
            'continue_shopping': 'Tiếp tục mua hàng',
            'Invoice information': 'Thông tin hóa đơn',
            'Payment method': 'Phương pháp thanh toán',
            'Debit Amount': 'Số tiền nợ',
            'Payment Amount': 'Số tiền thanh toán',
            'pay_credit': 'Bạn phải thanh toán công nợ vượt để có thể đặt hàng',
            'pay_entire': 'Thanh toán số tiền yêu cầu bằng hình thức chuyển khoản',
            'Order Total': 'Tổng đơn hàng',
            'p_t_payment': 'Tổng đơn hàng',
            'DEBT': 'NỢ',
            'PAY': 'CHUYỂN KHOẢN',
            'ADVANCE': 'TRẢ TRƯỚC',
            'd_debit': 'Khách hàng đặt hàng bằng hình thức ghi nợ',
            'd_pay': 'Trả toàn bộ đơn hàng băng hình thức chuyển khoản',
            'd_advan': 'Khách hàng trả trước 70% khi đặt hàng và trả nốt 30% sau khi nhận hàng',
            'p_t_checkout': 'Tiến hành thanh toán',
            'Back': 'Quay lại',
            'Repurchase': 'Mua lại',
            'Milling': 'Phay',
            'Number Custom Declaration': 'Số lượng tờ khai',
            'Total Custom Declaration': 'Tổng phí mở tờ khai',
            'ADVANCE 2': ' ADVANCE',
            'Beneficiary': 'Người thụ hưởng',
            'Swift Code': 'Mã Swift',
        },
        'en_US': {
            'tku_for_pay': 'Thank you for ordering on Oristar. To pay for orders in the form of Pay, please transfer',
            'tku_for_advan': 'Thank you for ordering on Oristar. To pay for orders in the form of Advance, please transfer',
            'acc_syntax': 'according to the following syntax',
            '70_per_order': '70% of order total',
            'cp_ck': 'TT [Space] ORISTAR [ Phone ]',
            'acc_inf': 'ACCOUNT INFORMATION',
            'bank_name': 'Bank name',
            'bank_num': 'Account number',
            'Branch': 'Branch',
            'acc_own': 'Account owner',
            'Order': 'Order',
            'Order confirmation': 'Order confirmation',
            'submit_success_msg': 'Your order has been submitted successfully, ORISTAR will respond Review the information about the order and notify you within 24 hours by email and phone number',
            'tku_or_service': 'Thank you for using ORISTAR\'s service',
            'back_to_hp': 'Go back to homepage',
            'continue_shopping': 'Continue shopping',
            'Invoice information': 'Invoice information',
            'Payment method': 'Payment method',
            'pay_credit': 'You need to pay the excess amount to be able to place an order',
            'pay_entire': 'Pay for the amount via transfer',
            'Order Total': 'Order Total',
            'p_t_payment': 'Proceed to the payment',
            'DEBT': 'DEBT',
            'PAY': 'PAY',
            'ADVANCE': 'ADVANCE',
            'd_debit': 'Customers order products via debit',
            'd_pay': 'Payment for the entire order via bank transfer',
            'd_advan': 'Customers pay 70% in advance when place an order and 30% payment after receiving the goods',
            'p_t_checkout': 'Proceed to the checkout',
            'Back': 'Back',
            'ADVANCE 2': ' ADVANCE'
        }
    }

    var translate_help = function(term, type =0) {
        term = term.trim();
        var lang = session.lang;
        var lang_term = terms[lang] ? terms[lang] : {};
        var translated = lang_term[term] ? lang_term[term] : term;
        if(typeof translated == 'object') {
            return translated[type]
        }
        return translated;
    }

    return translate_help;
});