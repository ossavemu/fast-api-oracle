-- Limpiar datos existentes en orden inverso a las dependencias
DELETE FROM recycling_app.ranking;
DELETE FROM recycling_app.reciclaje;
DELETE FROM recycling_app.bonos;
DELETE FROM recycling_app.premio;
DELETE FROM recycling_app.evento;
DELETE FROM recycling_app.usuario;
DELETE FROM recycling_app.tipo_reciclaje;

-- Reiniciar secuencias
ALTER SEQUENCE recycling_app.ranking_seq RESTART;
ALTER SEQUENCE recycling_app.reciclaje_seq RESTART;
ALTER SEQUENCE recycling_app.bonos_seq RESTART;
ALTER SEQUENCE recycling_app.premio_seq RESTART;
ALTER SEQUENCE recycling_app.evento_seq RESTART;
ALTER SEQUENCE recycling_app.usuario_seq RESTART;
ALTER SEQUENCE recycling_app.tipo_reciclaje_seq RESTART;

-- Insertar superusuario (id_perfil = 2 para admin)
INSERT INTO recycling_app.usuario (id_usuario, id_perfil, documento, telefono, nombre, apellido, correo, contrasena)
VALUES (
    recycling_app.usuario_seq.NEXTVAL, 
    2, 
    '00000000', 
    '3000000000', 
    'Super', 
    'Admin', 
    'sudo@admin.com',
    '$2b$12$lN2PZVxFigj3Qs/4ORZBUuqpBzlHJHhvKGHxbKqx9mnZ2K6ZDEYdG'  -- Hash correcto para ADMIN2024
);

-- Insertar usuarios de prueba
INSERT INTO recycling_app.usuario (id_usuario, id_perfil, documento, telefono, nombre, apellido, correo, contrasena)
VALUES (recycling_app.usuario_seq.NEXTVAL, 2, '12345678', '3001234567', 'Juan', 'Pérez', 'juan@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiGRH3nw5oby');

INSERT INTO recycling_app.usuario (id_usuario, id_perfil, documento, telefono, nombre, apellido, correo, contrasena)
VALUES (recycling_app.usuario_seq.NEXTVAL, 1, '87654321', '3007654321', 'Ana', 'López', 'ana@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiGRH3nw5oby');

-- Insertar tipos de reciclaje
INSERT INTO recycling_app.tipo_reciclaje (id_tipo_reciclaje, nombre, caracteristicas, puntos_botella)
VALUES (recycling_app.tipo_reciclaje_seq.NEXTVAL, 'Plástico', 'Botellas plásticas', 10);

INSERT INTO recycling_app.tipo_reciclaje (id_tipo_reciclaje, nombre, caracteristicas, puntos_botella)
VALUES (recycling_app.tipo_reciclaje_seq.NEXTVAL, 'Vidrio', 'Botellas de vidrio', 15);

INSERT INTO recycling_app.tipo_reciclaje (id_tipo_reciclaje, nombre, caracteristicas, puntos_botella)
VALUES (recycling_app.tipo_reciclaje_seq.NEXTVAL, 'Papel', 'Reciclaje de papel', 5);

INSERT INTO recycling_app.tipo_reciclaje (id_tipo_reciclaje, nombre, caracteristicas, puntos_botella)
VALUES (recycling_app.tipo_reciclaje_seq.NEXTVAL, 'Metal', 'Latas de metal', 20);

-- Insertar eventos
INSERT INTO recycling_app.evento (id_evento, id_usuario, id_tipo_reciclaje, nombre, lugar, h_inicio, h_final, fecha, observaciones)
VALUES (
    recycling_app.evento_seq.NEXTVAL, 
    1, -- Juan es el organizador
    1, -- Tipo plástico
    'Reciclatón 2024', 
    'Parque Central',
    TO_DATE('2024-03-15 09:00', 'YYYY-MM-DD HH24:MI'),
    TO_DATE('2024-03-15 17:00', 'YYYY-MM-DD HH24:MI'),
    TO_DATE('2024-03-15', 'YYYY-MM-DD'),
    'Gran evento de reciclaje'
);

INSERT INTO recycling_app.evento (id_evento, id_usuario, id_tipo_reciclaje, nombre, lugar, h_inicio, h_final, fecha, observaciones)
VALUES (
    recycling_app.evento_seq.NEXTVAL,
    2, -- Ana es la organizadora
    2, -- Tipo vidrio
    'EcoFest 2024',
    'Plaza Mayor',
    TO_DATE('2024-04-20 10:00', 'YYYY-MM-DD HH24:MI'),
    TO_DATE('2024-04-20 18:00', 'YYYY-MM-DD HH24:MI'),
    TO_DATE('2024-04-20', 'YYYY-MM-DD'),
    'Festival ecológico'
);

-- Insertar bonos para los eventos
INSERT INTO recycling_app.bonos (id_bono, id_evento, descripcion, valor_puntos)
VALUES (recycling_app.bonos_seq.NEXTVAL, 1, 'Bono por primera participación', 50);

INSERT INTO recycling_app.bonos (id_bono, id_evento, descripcion, valor_puntos)
VALUES (recycling_app.bonos_seq.NEXTVAL, 1, 'Bono por traer más de 10 items', 100);

INSERT INTO recycling_app.bonos (id_bono, id_evento, descripcion, valor_puntos)
VALUES (recycling_app.bonos_seq.NEXTVAL, 2, 'Bono madrugador', 75);

-- Insertar premios para los eventos
INSERT INTO recycling_app.premio (id_premio, id_evento, descripcion_premio)
VALUES (recycling_app.premio_seq.NEXTVAL, 1, 'Kit de reciclaje profesional para el primer lugar');

INSERT INTO recycling_app.premio (id_premio, id_evento, descripcion_premio)
VALUES (recycling_app.premio_seq.NEXTVAL, 1, 'Set de contenedores ecológicos para el segundo lugar');

INSERT INTO recycling_app.premio (id_premio, id_evento, descripcion_premio)
VALUES (recycling_app.premio_seq.NEXTVAL, 2, 'Curso de reciclaje avanzado');

-- Insertar algunos reciclajes
INSERT INTO recycling_app.reciclaje (id_reciclaje, id_evento, id_usuario, cantidad, puntos, puntos_bono, puntos_totales)
VALUES (recycling_app.reciclaje_seq.NEXTVAL, 1, 2, 15, 150, 50, 200);

INSERT INTO recycling_app.reciclaje (id_reciclaje, id_evento, id_usuario, cantidad, puntos, puntos_bono, puntos_totales)
VALUES (recycling_app.reciclaje_seq.NEXTVAL, 1, 1, 20, 200, 100, 300);

INSERT INTO recycling_app.reciclaje (id_reciclaje, id_evento, id_usuario, cantidad, puntos, puntos_bono, puntos_totales)
VALUES (recycling_app.reciclaje_seq.NEXTVAL, 2, 2, 10, 150, 75, 225);

-- Insertar rankings
INSERT INTO recycling_app.ranking (id_ranking, id_usuario, id_reciclaje, id_evento, id_premio, puntaje_total, posicion)
VALUES (recycling_app.ranking_seq.NEXTVAL, 1, 2, 1, 1, 300, 1);

INSERT INTO recycling_app.ranking (id_ranking, id_usuario, id_reciclaje, id_evento, id_premio, puntaje_total, posicion)
VALUES (recycling_app.ranking_seq.NEXTVAL, 2, 1, 1, 2, 200, 2);

INSERT INTO recycling_app.ranking (id_ranking, id_usuario, id_reciclaje, id_evento, NULL, puntaje_total, posicion)
VALUES (recycling_app.ranking_seq.NEXTVAL, 2, 3, 2, NULL, 225, 1);

COMMIT;

-- Verificar datos insertados
SELECT 'Usuarios' as tabla, COUNT(*) as total FROM recycling_app.usuario
UNION ALL
SELECT 'Tipos de Reciclaje', COUNT(*) FROM recycling_app.tipo_reciclaje
UNION ALL
SELECT 'Eventos', COUNT(*) FROM recycling_app.evento
UNION ALL
SELECT 'Bonos', COUNT(*) FROM recycling_app.bonos
UNION ALL
SELECT 'Premios', COUNT(*) FROM recycling_app.premio
UNION ALL
SELECT 'Reciclajes', COUNT(*) FROM recycling_app.reciclaje
UNION ALL
SELECT 'Rankings', COUNT(*) FROM recycling_app.ranking;

-- Mostrar detalles de eventos con sus bonos y premios
SELECT 
    e.nombre as evento,
    e.lugar,
    e.fecha,
    t.nombre as tipo_reciclaje,
    u.nombre || ' ' || u.apellido as organizador,
    (SELECT COUNT(*) FROM recycling_app.bonos b WHERE b.id_evento = e.id_evento) as total_bonos,
    (SELECT COUNT(*) FROM recycling_app.premio p WHERE p.id_evento = e.id_evento) as total_premios
FROM recycling_app.evento e
JOIN recycling_app.tipo_reciclaje t ON e.id_tipo_reciclaje = t.id_tipo_reciclaje
JOIN recycling_app.usuario u ON e.id_usuario = u.id_usuario
ORDER BY e.fecha;

-- Mostrar ranking general
SELECT 
    u.nombre || ' ' || u.apellido as participante,
    COUNT(r.id_reciclaje) as total_reciclajes,
    SUM(r.puntos_totales) as puntos_totales,
    RANK() OVER (ORDER BY SUM(r.puntos_totales) DESC) as posicion
FROM recycling_app.usuario u
JOIN recycling_app.reciclaje r ON u.id_usuario = r.id_usuario
GROUP BY u.id_usuario, u.nombre, u.apellido
ORDER BY puntos_totales DESC;

EXIT; 