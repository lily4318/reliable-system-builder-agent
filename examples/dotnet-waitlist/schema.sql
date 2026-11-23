PRAGMA foreign_keys = ON;

CREATE TABLE booking (
    id INTEGER PRIMARY KEY CHECK (id > 0),
    slot_id INTEGER NOT NULL CHECK (slot_id > 0),
    queue_sequence INTEGER NOT NULL CHECK (queue_sequence > 0),
    eligible INTEGER NOT NULL CHECK (eligible IN (0, 1)),
    status TEXT NOT NULL CHECK (status IN ('waiting', 'confirmed', 'cancelled')),
    CHECK (status <> 'confirmed' OR eligible = 1)
);

CREATE UNIQUE INDEX one_confirmed_booking_per_slot
    ON booking (slot_id) WHERE status = 'confirmed';

CREATE INDEX eligible_queue
    ON booking (slot_id, queue_sequence, id) WHERE status = 'waiting' AND eligible = 1;

CREATE TABLE cancellation (
    booking_id INTEGER PRIMARY KEY REFERENCES booking (id),
    promoted_id INTEGER REFERENCES booking (id),
    CHECK (promoted_id IS NULL OR booking_id <> promoted_id)
);
