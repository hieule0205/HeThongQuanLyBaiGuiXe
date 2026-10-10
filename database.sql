CREATE DATABASE IF NOT EXISTS quan_ly_bai_xe;
USE quan_ly_bai_xe;

CREATE TABLE lich_su_gui_xe (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bien_so VARCHAR(20) NOT NULL,
    loai_xe VARCHAR(20) NOT NULL,
    thoi_gian_vao DATETIME NOT NULL,
    thoi_gian_ra DATETIME DEFAULT NULL,
    tien_phi INT DEFAULT NULL,
    trang_thai VARCHAR(30) NOT NULL
);