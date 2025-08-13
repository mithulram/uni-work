#include <asoa_security_middleware/networking/communication.h>
#include <configuration.h>

#define NR_SALTS 4
#define NR_SEC_EXCEPTS 1

Salt salts[NR_SALTS] = {{{0x8c, 0x97, 0xb7, 0xd8, 0x9a, 0xdb, 0x8b, 0xd8, 0x6c,
                          0x9f, 0xa5, 0x62, 0x70, 0x4c, 0xe4, 0x0e}},
                        {{0x6a, 0xff, 0xb8, 0xee, 0x00, 0x20, 0x4d, 0xff, 0x25,
                          0x3c, 0x17, 0x65, 0x2f, 0x63, 0x58, 0xab}},
                        {{0x6f, 0x2f, 0x06, 0xee, 0x8c, 0xf2, 0x6f, 0x7c, 0x6b,
                          0x52, 0x54, 0x27, 0x34, 0xb2, 0x9e, 0x1e}},
                        {{0x8d, 0x12, 0xb5, 0xd7, 0x4a, 0x1f, 0x82, 0x91, 0xe4,
                          0x6f, 0xe5, 0x04, 0x20, 0x0a, 0x35, 0x3f}}};

SecurityException exceptions[NR_SEC_EXCEPTS] = {
    {{{{0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00}},
      {{0x00, 0x01, 0x00, 0xC2}},
      true,
      false},
     false,
     false,
     10}};

Configuration CONFIG_AS_LIB = {
    .ecu_id = 11,
    .max_num_incidents = 20,
    .ecu_name = "SensorModule",

    .security_platform.ip = "10.0.0.28",
    .security_platform.port = 4451,
    .security_platform.protocol = UDP,
    .security_platform.connection_attempts = 3,
    .security_platform.broadcast_port = 4412,
    .security_platform.broadcast_timeout = 15000,

    .log_server.ip = "10.0.0.28",
    .log_server.port = 8081,
    .log_server.protocol = UDP,
    .log_server.connection_attempts = 3,
    .log_server.broadcast_port = 4411,
    .log_server.broadcast_timeout = 15000,

    .config_server.ip = "10.0.0.28",
    .config_server.port = 4420,
    .config_server.protocol = UDP,
    .config_server.connection_attempts = 3,
    .config_server.broadcast_port = 4410,
    .config_server.broadcast_timeout = 15000,

    .root_key = {{0x60, 0x13, 0x6d, 0x34, 0xee, 0xa1, 0x8a, 0x52, 0xeb, 0x35, 0x80, 0xef, 0xd2, 0xd0, 0x0b, 0x57}},
    .fallback_key = {{0x2c, 0x58, 0x15, 0x56, 0x77, 0xef, 0x42, 0x6f, 0xec,
                      0xf7, 0x8c, 0xaf, 0x3f, 0x1a, 0x68, 0xbc}},

    .nr_salts = NR_SALTS,
    .salts = salts,

    .is_dummy_config = false,
    .security_enabled = true,
    .verification_enabled = true,
    .use_ipc = false,
    .print_keys = true,
    .log_level = INFO,

    .security_exceptions = exceptions,
    .nr_security_exceptions = NR_SEC_EXCEPTS
};
