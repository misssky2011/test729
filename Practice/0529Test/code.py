import qrcode

def generate_qr_code():
    data = input("请输入你要生成的二维码")
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    img.save('qrcode.png') #保存二维码图片文件

    print("二维码已生成并保存位qrcode.png文件。")

generate_qr_code()