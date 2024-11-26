CREATE TABLE recycling_app.usuario(
    id_usuario NUMBER PRIMARY KEY,
    id_perfil NUMBER,
    documento varchar (20) NOT NULL,
    telefono Varchar(20) NOT NULL,
    nombre Varchar(20) NOT NULL,
    apellido Varchar(20) NOT NULL,
    correo Varchar(30) NOT NULL,
    contrasena Varchar(100) NOT NULL    
);

-- Secuencia para tipo_reciclaje
CREATE SEQUENCE recycling_app.tipo_reciclaje_seq
START WITH 1
INCREMENT BY 1;

CREATE TABLE recycling_app.tipo_reciclaje (
    id_tipo_reciclaje NUMBER NOT NULL,
    nombre VARCHAR2(20) NOT NULL UNIQUE,
    caracteristicas VARCHAR2(50) NOT NULL,
    puntos_botella INT NOT NULL,
    PRIMARY KEY (id_tipo_reciclaje)
);

CREATE TABLE recycling_app.evento (
    id_evento NUMBER NOT NULL,
    id_usuario NUMBER,
    id_tipo_reciclaje NUMBER,
    nombre VARCHAR2(20) NOT NULL,
    lugar VARCHAR2(20) NOT NULL,
    h_inicio DATE NOT NULL,
    h_final DATE NOT NULL,
    fecha DATE NOT NULL,
    observaciones VARCHAR2(100),
    PRIMARY KEY (id_evento),
    FOREIGN KEY (id_usuario) REFERENCES recycling_app.usuario(id_usuario),
    FOREIGN KEY (id_tipo_reciclaje) REFERENCES recycling_app.tipo_reciclaje(id_tipo_reciclaje)
);

CREATE TABLE recycling_app.reciclaje (
    id_reciclaje NUMBER PRIMARY KEY,
    id_evento NUMBER,
    id_usuario NUMBER,
    cantidad NUMBER NOT NULL,
    puntos NUMBER NOT NULL,
    puntos_bono NUMBER NOT NULL,
    puntos_totales NUMBER NOT NULL,
    FOREIGN KEY (id_evento) REFERENCES recycling_app.evento(id_evento),
    FOREIGN KEY (id_usuario) REFERENCES recycling_app.usuario(id_usuario)
);

CREATE TABLE recycling_app.premio (
    id_premio INT NOT NULL,
    id_evento INT,
    descripcion_premio CLOB NOT NULL,
    PRIMARY KEY (id_premio),
    FOREIGN KEY (id_evento) REFERENCES recycling_app.evento(id_evento)
);

CREATE TABLE recycling_app.ranking (
    id_ranking INT NOT NULL,
    id_usuario INT,
    id_reciclaje INT,
    id_evento INT,
    id_premio INT,
    puntaje_total INT NOT NULL,
    posicion INT NOT NULL,
    PRIMARY KEY (id_ranking),
    FOREIGN KEY (id_usuario) REFERENCES recycling_app.usuario(id_usuario),
    FOREIGN KEY (id_reciclaje) REFERENCES recycling_app.reciclaje(id_reciclaje),
    FOREIGN KEY (id_evento) REFERENCES recycling_app.evento(id_evento),
    FOREIGN KEY (id_premio) REFERENCES recycling_app.premio(id_premio)
);

CREATE TABLE recycling_app.bonos (
    id_bono NUMBER NOT NULL,
    id_evento INT,
    descripcion VARCHAR2(120) NOT NULL,
    valor_puntos INT NOT NULL,
    PRIMARY KEY (id_bono),
    FOREIGN KEY (id_evento) REFERENCES recycling_app.evento(id_evento)
);

-- Crear secuencias
CREATE SEQUENCE recycling_app.evento_seq
    START WITH 1
    INCREMENT BY 1
    NOCACHE
    NOCYCLE;

CREATE SEQUENCE recycling_app.usuario_seq
    START WITH 1
    INCREMENT BY 1
    NOCACHE
    NOCYCLE;

CREATE SEQUENCE recycling_app.tipo_reciclaje_seq
    START WITH 1
    INCREMENT BY 1
    NOCACHE
    NOCYCLE;

CREATE SEQUENCE recycling_app.reciclaje_seq
    START WITH 1
    INCREMENT BY 1
    NOCACHE
    NOCYCLE;

CREATE SEQUENCE recycling_app.ranking_seq
    START WITH 1
    INCREMENT BY 1
    NOCACHE
    NOCYCLE;

CREATE SEQUENCE recycling_app.bonos_seq
    START WITH 1
    INCREMENT BY 1
    NOCACHE
    NOCYCLE;

CREATE SEQUENCE recycling_app.premio_seq
    START WITH 1
    INCREMENT BY 1
    NOCACHE
    NOCYCLE;

-- Insertar datos en orden correcto
INSERT INTO recycling_app.usuario (id_usuario, id_perfil, documento, telefono, nombre, apellido, correo, contrasena)
VALUES (1, 2, '12345678', '5551234567', 'Juan', 'Pérez', 'juan.perez@example.com', 'hashedpassword123');

INSERT INTO recycling_app.usuario (id_usuario, id_perfil, documento, telefono, nombre, apellido, correo, contrasena)
VALUES (2, 1, '87654321', '5559876543', 'Ana', 'López', 'ana.lopez@example.com', 'hashedpassword456');

-- Insertar tipos de reciclaje únicos
INSERT INTO recycling_app.tipo_reciclaje (id_tipo_reciclaje, nombre, caracteristicas, puntos_botella)
VALUES (recycling_app.tipo_reciclaje_seq.NEXTVAL, 'Plástico', 'Botellas plásticas', 10);

INSERT INTO recycling_app.tipo_reciclaje (id_tipo_reciclaje, nombre, caracteristicas, puntos_botella)
VALUES (recycling_app.tipo_reciclaje_seq.NEXTVAL, 'Vidrio', 'Botellas de vidrio', 15);

INSERT INTO recycling_app.tipo_reciclaje (id_tipo_reciclaje, nombre, caracteristicas, puntos_botella)
VALUES (recycling_app.tipo_reciclaje_seq.NEXTVAL, 'Papel', 'Reciclaje de papel', 5);

INSERT INTO recycling_app.tipo_reciclaje (id_tipo_reciclaje, nombre, caracteristicas, puntos_botella)
VALUES (recycling_app.tipo_reciclaje_seq.NEXTVAL, 'Metal', 'Latas de metal', 20);

-- Los demás INSERT se agregarán después de verificar que la estructura básica funciona

-- Tabla para registrar los bonos utilizados en cada reciclaje
CREATE TABLE recycling_app.reciclaje_bonos (
    id_reciclaje NUMBER,
    id_bono NUMBER,
    PRIMARY KEY (id_reciclaje, id_bono),
    FOREIGN KEY (id_reciclaje) REFERENCES recycling_app.reciclaje(id_reciclaje),
    FOREIGN KEY (id_bono) REFERENCES recycling_app.bonos(id_bono)
);
