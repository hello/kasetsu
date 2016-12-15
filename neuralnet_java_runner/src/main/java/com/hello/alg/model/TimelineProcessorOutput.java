package com.hello.alg.model;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.hello.suripu.core.models.Event;
import com.hello.suripu.core.models.SleepScore;
import com.hello.suripu.core.models.SleepStats;

import java.util.List;

/**
 * Created by benjo on 12/14/16.
 */
public class TimelineProcessorOutput {

    @JsonProperty("events")
    public final List<Event> events;

    @JsonProperty("feedback_events")
    public final List<Event> feedbackEvents;

    @JsonProperty("sleep_stats")
    public final SleepStats sleepStats;

    @JsonProperty("sleep_score")
    public final SleepScore sleepScore;

    @JsonCreator
    public TimelineProcessorOutput(@JsonProperty("events") final List<Event> events,
                                   @JsonProperty("feedback_events") final List<Event> feedbackEvents,
                                   @JsonProperty("sleep_stats") final SleepStats sleepStats,
                                   @JsonProperty("sleep_score") final SleepScore sleepScore) {
        this.events = events;
        this.feedbackEvents = feedbackEvents;
        this.sleepStats = sleepStats;
        this.sleepScore = sleepScore;
    }




}
