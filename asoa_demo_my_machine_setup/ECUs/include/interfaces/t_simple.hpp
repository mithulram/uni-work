#pragma once


#include <asoa/core/functionality.hpp>


class FloatTopic : public Functionality {
	protected:
		std::string topic_name;
		uint64_t topic_id;
		
	public:
        FloatTopic() : Functionality(){

        }

        const std::string& getTypeName() override {
            return topic_name;
        }

        std::uint32_t getTypeID() override {
            return topic_id;
        }

		// This struct holds the topic data and provides means of (de)serialization.
		struct Data : public FuncComponentBase {
			float topic_data;
			uint32_t maxSize() override {
                return ucdr_alignment(0,4)+4;
			}
			bool deserialize(const uint8_t* buffer, uint32_t length) override {
                ucdrBuffer ucdr_buffer;
                ucdr_init_buffer(&ucdr_buffer, buffer, length);
                ucdr_deserialize_float(&ucdr_buffer, &topic_data);
                return !ucdr_buffer.error;
			}
			long serialize(uint8_t* buffer, uint32_t max_size) override {

                ucdrBuffer ucdr_buffer;
                ucdr_init_buffer(&ucdr_buffer, buffer, max_size);
                ucdr_serialize_float(&ucdr_buffer, topic_data);
                return ucdr_buffer.error ? -1 : ucdr_buffer_length(&ucdr_buffer);
			}
		} data_;

		struct Quality : public FuncComponentBase {
			float current_accuracy;
			bool deserialize(const uint8_t* buffer, uint32_t length) override {
				ucdrBuffer ucdr_buffer;
				ucdr_init_buffer(&ucdr_buffer, buffer, length);
				ucdr_deserialize_float(&ucdr_buffer, &current_accuracy);
				return !ucdr_buffer.error;
			}
			long serialize(uint8_t* buffer, uint32_t max_size) override {
				ucdrBuffer ucdr_buffer;
				ucdr_init_buffer(&ucdr_buffer, buffer, max_size);
				ucdr_serialize_float(&ucdr_buffer, current_accuracy);
				return ucdr_buffer.error ? -1 : ucdr_buffer_length(&ucdr_buffer);
			}
			uint32_t maxSize() override {
				uint32_t size = 0;
				uint32_t previous_size = 0;
				size += ucdr_alignment(size, 4) + 4;
				return size - previous_size;
			}
		} quality_;
		
		// This struct ensures QoS by providing parameters to allow a requirement to assess the quality of data received by a guarantee.
		struct Parameter : public FuncComponentBase {
			float expected_data;
			float expected_update_rate;
			bool deserialize(const uint8_t* buffer, uint32_t length) override {
				ucdrBuffer ucdr_buffer;
				ucdr_init_buffer(&ucdr_buffer, buffer, length);
				ucdr_deserialize_float(&ucdr_buffer, &expected_data);
				ucdr_deserialize_float(&ucdr_buffer, &expected_data);
				return !ucdr_buffer.error;
			}
			long serialize(uint8_t* buffer, uint32_t max_size) override {
				ucdrBuffer ucdr_buffer;
				ucdr_init_buffer(&ucdr_buffer, buffer, max_size);
				ucdr_serialize_float(&ucdr_buffer, expected_data);
				ucdr_serialize_float(&ucdr_buffer, expected_update_rate);
				return ucdr_buffer.error ? -1 : ucdr_buffer_length(&ucdr_buffer); 
			}
			uint32_t maxSize() override {
				uint32_t size = 0;
				uint32_t previous_size = size;
				size += ucdr_alignment(size, 4) + 4;
				size += ucdr_alignment(size, 4) + 4;
				return size - previous_size;
			}
		} parameter_;

};
